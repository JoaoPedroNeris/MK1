# v0.2c: paredes dos insertos e furos do horn corrigidos (18/11/2026)

Substituem as versões de `v0.2/stl/` e `v0.2/stl/cabos/` destas peças. STL exatos (gerados por `cad/exportar_stl.py`, sem aproximação de malha).

| Peça | Qtd | O que mudou |
| --- | --- | --- |
| upper_arm.stl | 1 | Furos do horn nas 2 placas do garfo do ombro (faltavam). Bolso do cotovelo com paredes de ponta 10,6 / 9,6 mm e ponta arredondada R25. Bloco junto ao garfo 9,5 mm. Rasgo do cabo do servo em y +5 a +15. |
| forearm.stl | 1 | Igual ao braço (bolso do punho, bloco, rasgo). |
| turret.stl | 1 | 2 bolsos do ombro com as paredes novas; furo de acesso ao parafuso do horn de giro 9 para 6,5 mm. Frente do pedestal no mesmo lugar. |
| servo_cap.stl | 3 | Acompanha o bolso novo; o parafuso da frente ficou sem rebaixo (a cabeça apoia em cima). |
| upper_cover.stl, fore_cover.stl | 1 cada | Furo da ponta do bolso acompanha o inserto novo (2,3 mm mais para trás). |
| base_shell.stl | 1 | Colunas dos cantos com raio 5,5 mm (antes 5). |

Furo central do horn nos garfos: 6,5 mm (antes 9). Confira com o servo na mão se a cabeça do parafuso central do horn passa.

Paredes (mínimo em volta de cada inserto M3): bolso 2,7 (frente) e 3,2 (trás); tampa de baixo 4,4 e 2,9; base 3,4; torre 3,6. Faixa de movimento igual à v0.2b: ombro -27,5 a +117,5, cotovelo e punho sem perda (o cotovelo continua limitado a -105 pelas presilhas).

A garra_base (Fusion) ainda tem o furo central do horn de 9 mm; ela funciona assim (parede 0,85 mm entre o furo central e os furos M3, são furos passantes).
