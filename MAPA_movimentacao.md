# Mapa da reorganização (18/11/2026)

Nada foi apagado. Cada linha diz onde o arquivo estava e para onde foi. Caminhos relativos a `C:\Users\jpinh\MK1`.

## Movidos de dentro da pasta (v0.2 → nova estrutura)

| Antes | Agora |
| --- | --- |
| v0.2/stl/fit_coupon_v02b.stl | 01_imprimir/00_teste_primeiro/fit_coupon_v02b.stl |
| v0.2/stl/v02c/base_shell.stl | 01_imprimir/01_base/base_shell.stl |
| v0.2/stl/v02c/turret.stl | 01_imprimir/01_base/turret.stl |
| v0.2/stl/v02c/upper_arm.stl | 01_imprimir/02_braco/upper_arm.stl |
| v0.2/stl/v02c/forearm.stl | 01_imprimir/02_braco/forearm.stl |
| v0.2/stl/v02c/upper_cover.stl | 01_imprimir/02_braco/upper_cover.stl |
| v0.2/stl/v02c/fore_cover.stl | 01_imprimir/02_braco/fore_cover.stl |
| v0.2/stl/v02c/servo_cap.stl | 01_imprimir/02_braco/servo_cap_x3.stl |
| v0.2/stl/cabos/garra_base.stl | 01_imprimir/03_garra/garra_base.stl |
| v0.2/stl/garra/carcaca.stl | 01_imprimir/03_garra/carcaca.stl |
| v0.2/stl/garra/disco_espiral.stl | 01_imprimir/03_garra/disco_espiral.stl |
| v0.2/stl/garra/placa_guia.stl | 01_imprimir/03_garra/placa_guia.stl |
| v0.2/stl/garra/mordente_1/2/3.stl | 01_imprimir/03_garra/mordente_1/2/3.stl |
| v0.2/stl/garra/ponta_TPU_1/2/3.stl | 01_imprimir/03_garra/ponta_TPU_1/2/3.stl |
| v0.2/stl/cabos/presilha_cabo.stl | 01_imprimir/04_cabos/presilha_cabo_x7.stl |
| v0.2/cad/assembly.py, csg_manifold.py, exportar_stl.py, params.py, parts.py | 02_cad_fonte/cad/ (mesmos nomes) |
| v0.2/scripts/fit_coupon_v02.py, garra_v02.py, importar_montagem_v02.py | 02_cad_fonte/fusion_scripts/ (mesmos nomes, caminhos atualizados) |
| v0.2/stl/v02c/README.md | 03_docs/mudancas_v02c_paredes.md |
| v0.2/cabos/README.md | 03_docs/passa_cabos.md |
| v0.2/stl/v02c/corte_bolso_antes_depois.png | 04_imagens/corte_bolso_antes_depois.png |
| v0.2/cabos/proposta_canaletas.png | 04_imagens/cabos_proposta_canaletas.png |
| v0.2/cabos/montagem_presilhas.png | 04_imagens/cabos_montagem_presilhas.png |
| v0.2/montagem_b/ (48 arquivos) | 05_visualizacao_fusion/montagem_b/ |
| v0.2/montagem/ (44 arquivos, versão com mastro e mola) | 99_arquivo/v0.2_original/montagem_v02a_com_mastro_OBSOLETA/ |
| v0.2/stl/fit_coupon.stl | 99_arquivo/v0.2_original/stl_obsoletos/fit_coupon_v01_OBSOLETO.stl |
| v0.2/stl/fit_coupon_v02.stl | 99_arquivo/v0.2_original/stl_obsoletos/fit_coupon_v02_com_mastro_OBSOLETO.stl |
| v0.2/stl/garra/garra_base.stl (versão sem o inserto da presilha) | 99_arquivo/v0.2_original/stl_obsoletos/garra_base_v02b_sem_presilha_OBSOLETO.stl |
| v0.2/stl/cabos/turret.stl | 99_arquivo/v0.2_original/stl_obsoletos/turret_v02b_cabos_OBSOLETO.stl |
| v0.2/stl/cabos/upper_cover.stl | 99_arquivo/v0.2_original/stl_obsoletos/upper_cover_v02b_cabos_OBSOLETO.stl |
| v0.2/stl/cabos/fore_cover.stl | 99_arquivo/v0.2_original/stl_obsoletos/fore_cover_v02b_cabos_OBSOLETO.stl |

Por que `turret`, `upper_cover` e `fore_cover` de `stl/cabos` foram para o arquivo: a v0.2c (`stl/v02c`) foi gerada depois, a partir do mesmo `params.py` que já tinha o passa-cabos, e o README da v0.2c diz que ela substitui as de `stl/cabos`.

Por que a `garra_base` de `stl/garra` foi para o arquivo: era diferente da de `stl/cabos` (a de cabos é a que tem o inserto da presilha do punho). Conferido por checksum.

## Trazidos dos arquivos do Projeto (não estavam no notebook)

| Origem (arquivos do Projeto) | Agora |
| --- | --- |
| v0.2/cad/csg.py, build.py, analysis.py, render.py, eletronica_v02.py, montagem_v02.py, out/analysis.json | 02_cad_fonte/cad/ (sem `csg.py` o `exportar_stl.py` não rodava) |
| v0.2/cupom_tabela.md | 03_docs/cupom_teste_folgas.md |
| v0.2/auditoria/ (inteira) | 03_docs/auditoria/ |
| v0.2/garra_v0.2_esboco.png, garra_v02b_frente.png, garra_v02b_punho.png, montagem_v02b_iso.png, montagem_v02b_ombro_duplo.png | 04_imagens/ |
| v0.2/eletronica/base_por_dentro.png, base_vista_cima.png | 04_imagens/eletronica_*.png |
| v0.2/montagem_v02_iso.png, montagem_v02_lateral.png, montagem_v02_sem_mastro.png | 99_arquivo/imagens_antigas/ |
| v0.2/cad/backup_v02b_antes_paredes/ | 99_arquivo/backup_v02b_antes_paredes/ |
| README.md, params.py, parts.py, assembly.py, analysis.py, build.py, csg.py, render.py (raiz, v0.1) | 99_arquivo/v0.1/ (README virou README_v01.md) |

## Novos

| Arquivo | O que é |
| --- | --- |
| 01_imprimir/02_braco/upper_armor_x2.stl, fore_armor_x2.stl | Placas laranja do braço e do antebraço. Antes só existiam como malha de visualização. Exportadas em 18/11 do `parts.py` atual com o mesmo método da v0.2c (estanques, 3,3 mm de espessura, simétricas). |
| README.md | Guia da pasta. |
| MAPA_movimentacao.md | Este arquivo. |

## Caminhos ajustados nos scripts

| Script | Mudança |
| --- | --- |
| fusion_scripts/fit_coupon_v02.py | Salva em `01_imprimir/00_teste_primeiro` (antes `v0.2/stl`). |
| fusion_scripts/garra_v02.py | Salva a garra_base em `01_imprimir/03_garra` (antes `v0.2/stl/cabos`). |
| fusion_scripts/importar_montagem_v02.py | Lê de `05_visualizacao_fusion/montagem_b`. |
| cad/montagem_v02.py | Lê a garra de `01_imprimir/03_garra`; grava em `05_visualizacao_fusion/montagem_b`. |
| 03_docs/auditoria/auditoria.py, cargas.py, insertos.py | Importam de `02_cad_fonte/cad`; auditoria.py lê a garra de `01_imprimir/03_garra`. |
