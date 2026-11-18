"""
Verificacoes de engenharia a partir do proprio CAD:
  1. massa e centro de massa de cada elo (pecas + servos + eletronica);
  2. torque no ombro, cotovelo e punho em todas as poses da grade;
  3. escolha da mola de compensacao do ombro;
  4. faixa de movimento livre de cada junta (colisao peca contra peca).

Uso: python analysis.py   (grava out/analysis.json)
"""
import json
import os
import numpy as np
import assembly as A
from csg import mass_props, sample_inside
from params import *

G = 9.81
NOMINAL = 10.0 * G * 10      # 10 kg.cm em N.mm (torque nominal do STS3215 12 V)
PEAK = 30.0 * G * 10
PAYLOAD = 0.100              # kg
HW_MASS = {"sts3215": SV_MASS, "mg90s": MS_MASS, "hcsr04": 8.5}

ZERO = dict(yaw=0, shoulder=0, elbow=0, wrist=0, curl1=10, curl2=10)


def group_props():
    """Massa (kg) e CG (x, z) de cada grupo no referencial do proprio elo."""
    items = A.build(ZERO)
    f = A.frames(dict(A.DEFAULT_POSE, **ZERO))
    link_frame = {"upper": f["upper"], "fore": f["fore"], "hand": f["hand"]}
    out = {}
    for g, fm in link_frame.items():
        inv = np.linalg.inv(fm)
        mtot, mom = 0.0, np.zeros(3)
        for name, node, color, printed, grp, m in items:
            if grp != g:
                continue
            if printed:
                _, qty, proc, mat, rho, fill, _ = A.PARTS[name]
                vol, cg_local = mass_props(A.part(name), n=150_000)
                mass = vol * rho * fill / 1000.0
                cg_w = m @ np.r_[cg_local, 1.0]
            elif name in HW_MASS:
                mass = HW_MASS[name] / 1000.0
                lo, hi = node.aabb()
                cg_w = np.r_[(lo + hi) / 2, 1.0]
            else:
                continue
            mtot += mass
            mom += mass * (inv @ cg_w)[:3]
        out[g] = (mtot, mom / mtot)
    return out


def arm_points(props, th1, th2, th3, payload=True):
    """Pontos de massa no plano do braco, origem no eixo do ombro."""
    a1 = np.radians(th1)
    a2 = a1 + np.radians(th2)
    a3 = a2 + np.radians(th3)

    def rot(x, z, a):
        return x * np.cos(a) - z * np.sin(a), x * np.sin(a) + z * np.cos(a)

    elbow = np.array(rot(L1, 0, a1))
    wrist = elbow + np.array(rot(L2, 0, a2))
    pts = []
    m, c = props["upper"]; pts.append(("upper", m, np.array(rot(c[0], c[2], a1))))
    m, c = props["fore"]; pts.append(("fore", m, elbow + np.array(rot(c[0], c[2], a2))))
    m, c = props["hand"]; pts.append(("hand", m, wrist + np.array(rot(c[0], c[2], a3))))
    if payload:
        pts.append(("payload", PAYLOAD, wrist + np.array(rot(KNUCKLE_X + 30, 0, a3))))
    return pts, elbow, wrist


def gravity_torques(props, th1, th2, th3, payload=True):
    """Torque (N.mm) que a gravidade faz em cada junta; positivo = levanta."""
    pts, elbow, wrist = arm_points(props, th1, th2, th3, payload)
    ts = -sum(m * G * p[0] for _, m, p in pts)
    te = -sum(m * G * (p[0] - elbow[0]) for n, m, p in pts if n != "upper")
    tw = -sum(m * G * (p[0] - wrist[0]) for n, m, p in pts if n in ("hand", "payload"))
    return ts, te, tw


def spring_torque(th1, a, b, k, L0, Fi):
    t = np.radians(np.asarray(th1, float))
    zl = BEAM_H / 2 + 6
    Ax, Az = b * np.cos(t) - zl * np.sin(t), b * np.sin(t) + zl * np.cos(t)
    dx, dz = SPRING_PX - Ax, a - Az
    L = np.hypot(dx, dz)
    F = np.where(L > L0, Fi + k * (L - L0), 0.0)
    Fx, Fz = F * dx / L, F * dz / L
    return Ax * Fz - Az * Fx, L


def collision_range(moving, fixed, to_fixed, angles, thresh=0.4, min_pts=25):
    """Primeiro angulo (em cada sentido) em que o elo movel invade o fixo."""
    pts = np.vstack([sample_inside(n, 60_000) if not isinstance(n, np.ndarray) else n for n in moving])
    res = {}
    for sign in (1, -1):
        last = 0.0
        for th in angles:
            th = sign * th
            q = to_fixed(pts, th)
            hit = sum(int((f.sdf(q) < -thresh).sum()) for f in fixed)
            if hit > min_pts:
                break
            last = th
        res["+" if sign > 0 else "-"] = last
    return res


def _pitch(p, th, offset):
    t = np.radians(th)
    c, s = np.cos(t), np.sin(t)
    x = p[:, 0] * c - p[:, 2] * s
    z = p[:, 0] * s + p[:, 2] * c
    return np.c_[x + offset[0], p[:, 1] + offset[1], z + offset[2]]


def joint_ranges():
    turret_fixed = [A.part("turret"), A.part("servo_cap").move(SHOULDER_X, 0, SHOULDER_Z)]
    upper_moving = [A.part("upper_arm"), A.part("upper_cover")]
    sh = collision_range(upper_moving, turret_fixed,
                         lambda p, th: _pitch(p, th, (SHOULDER_X, 0, SHOULDER_Z)), np.arange(0, 181, 2.5))
    upper_fixed = [A.part("upper_arm"), A.part("servo_cap").move(L1, 0, 0), A.part("upper_cover")]
    fore_moving = [A.part("forearm"), A.part("fore_cover")]
    el = collision_range(fore_moving, upper_fixed, lambda p, th: _pitch(p, th, (L1, 0, 0)), np.arange(0, 181, 2.5))
    fore_fixed = [A.part("forearm"), A.part("servo_cap").move(L2, 0, 0), A.part("fore_cover")]
    hand_moving = [A.part("palm"), A.part("palm_lid")]
    wr = collision_range(hand_moving, fore_fixed, lambda p, th: _pitch(p, th, (L2, 0, 0)), np.arange(0, 181, 2.5))
    return {"ombro": sh, "cotovelo": el, "punho": wr}


def spring_search(props, poses):
    base = np.array([gravity_torques(props, *p)[0] for p in poses])
    th1s = np.array([p[0] for p in poses])
    best = None
    for a in SPRING_A:
        for b in SPRING_B:
            _, Ls = spring_torque(np.linspace(th1s.min(), th1s.max(), 60), a, b, 1, 0, 0)
            for L0 in np.arange(30, 125, 5.0):
                if Ls.max() > 2.2 * L0:
                    continue  # mola esticaria alem do limite elastico (com cordinha, folga e permitida)
                for Fi in (0.0, 2.0, 4.0, 6.0):
                    for k in np.arange(0.05, 3.01, 0.05):
                        ts, _ = spring_torque(th1s, a, b, k, L0, Fi)
                        worst = np.max(np.abs(base + ts))
                        if best is None or worst < best[0]:
                            best = (worst, a, b, float(L0), Fi, float(k))
    return np.max(np.abs(base)), best


def main():
    out = {}
    props = group_props()
    out["grupos"] = {g: {"massa_g": round(m * 1000, 1), "cg_x_mm": round(c[0], 1), "cg_z_mm": round(c[2], 1)}
                     for g, (m, c) in props.items()}
    ranges = joint_ranges()
    out["faixa_livre_graus"] = ranges

    sh_lo = max(-10.0, ranges["ombro"]["-"]); sh_hi = min(95.0, ranges["ombro"]["+"])
    el_lo = max(-140.0, ranges["cotovelo"]["-"]); el_hi = min(30.0, ranges["cotovelo"]["+"])
    wr_lo = max(-100.0, ranges["punho"]["-"]); wr_hi = min(60.0, ranges["punho"]["+"])
    poses = [(t1, t2, t3, pl) for t1 in np.arange(sh_lo, sh_hi + 0.1, 5) for t2 in np.arange(el_lo, el_hi + 0.1, 10)
             for t3 in np.linspace(wr_lo, wr_hi, 5) for pl in (False, True)]
    tq = np.array([gravity_torques(props, *p) for p in poses])
    out["pior_torque_kgcm_sem_mola"] = {j: round(float(np.max(np.abs(tq[:, i]))) / (G * 10), 2)
                                        for i, j in enumerate(("ombro", "cotovelo", "punho"))}
    raw, best = spring_search(props, poses)
    worst, a, b, L0, Fi, k = best
    ts_s, Ls = spring_torque(np.linspace(sh_lo, sh_hi, 50), a, b, k, L0, Fi)
    out["mola"] = {"furo_coluna_mm_acima_do_eixo": a, "furo_braco_mm": b, "comprimento_livre_mm": L0,
                   "tensao_inicial_N": Fi, "constante_N_por_mm": round(k, 2),
                   "comprimento_min_max_mm": [round(float(Ls.min()), 1), round(float(Ls.max()), 1)],
                   "forca_max_N": round(float(Fi + k * (Ls.max() - L0)), 1),
                   "pior_torque_ombro_kgcm_com_mola": round(worst / (G * 10), 2)}
    out["limite_nominal_kgcm"] = 10.0
    stretched = gravity_torques(props, 0, 0, 0, True)
    out["braco_esticado_horizontal_kgcm"] = [round(v / (G * 10), 2) for v in stretched]
    pts, elbow, wrist = arm_points(props, 0, 0, 0)
    out["alcance_ponta_dedos_mm"] = round(float(wrist[0] + KNUCKLE_X + PH1 + PH2), 0)
    os.makedirs("out", exist_ok=True)
    with open("out/analysis.json", "w") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
