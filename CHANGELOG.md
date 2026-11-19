# Histórico de versões

Cada versão fechada vira uma tag no Git (`v0.2c`, `v0.3`, ...). Para baixar exatamente os arquivos de uma versão: aba **Releases/Tags** no GitHub, ou `git checkout v0.2c`.

## Depois da v0.2c (18/11/2026, ainda sem tag)
- `servo_cap` x4 (eram 4 bolsos e só 3 tampas): `servo_cap_x4.stl`, `assembly.py` com 4; lote 4 refatiado (3 tampas + base + 7 presilhas, 19 h 06, 283 g).
- Corte a laser da v0.2 (tampa laranja e placa preta, SVG + DXF) em `01_imprimir/05_laser_acrilico/`, gerado por `02_cad_fonte/cad/exportar_laser.py`.
- Mapa de parafusos e lista de compra de fixadores em `03_docs/mapa_parafusos_v02c.md`: frente da `servo_cap` M3×10, presilhas da torre/punho M3×12 (não M3×10), tampas de baixo M3×14.

## v0.2c (18/11/2026)
- Primeira versão no GitHub.
- Ombro duplo (2× STS3215, sem mola), 6 servos no total; tudo em parafuso M3; sem mastro de webcam.
- Garra de 3 pontas com disco espiral, abertura Ø30; `garra_base` com furo do horn de 6,5 mm e inserto da presilha do punho.
- Paredes dos insertos corrigidas (todas ≥ 2,7 mm); `servo_cap` v0.2d (frisos até POCKET_Z + 1,5).
- Passa-cabos com laço à mostra e 7 presilhas M3; cotovelo limitado a −105°.
- Lotes de impressão para Prusa MK3S+ em PETG (`01_imprimir/lotes/`, só os .3mf; o G-code sai do fatiador).
- Pendente: arquivo de corte a laser (placa e tampa da base) da v0.2.
