# MK I — braço de mesa com mão de 3 dedos (projeto 3D v0.1)

Braço de 4 juntas (giro da base, ombro, cotovelo, punho) com uma mão de 2 dedos e 1 polegar oposto. As peças são pretas e laranja, com visual industrial. Tudo é paramétrico: as medidas ficam em `cad/params.py`, e um comando regenera todas as peças.

![MK I](cad/out/render_mk1.png)

## O que tem aqui

| Pasta | Conteúdo |
| --- | --- |
| `cad/params.py` | Todas as medidas. Comece por aqui. |
| `cad/parts.py` | O desenho de cada peça, em código. |
| `cad/build.py` | Gera os arquivos de fabricação em `cad/out/`. |
| `cad/analysis.py` | Confere massas, torques, mola e faixa de movimento a partir do próprio CAD. |
| `cad/render.py` | Gera as imagens de prévia. |
| `cad/out/scad/` | Um `.scad` por peça e `assembly.scad` com a montagem colorida. |
| `cad/out/laser/` | Chapas da tampa e da placa de base em SVG (vermelho corta, preto grava). |
| `cad/out/parts.csv` | Medidas, volume e massa estimada de cada peça. |
| `cad/out/analysis.json` | Resultado das verificações de engenharia. |

## Como gerar os STL

1. Instale o OpenSCAD (gratuito). Se o processamento ficar lento, use a versão de desenvolvimento e ative o motor Manifold nas preferências.
2. Abra `cad/out/scad/assembly.scad` e aperte F5 para ver a montagem.
3. Para cada peça, abra o `.scad`, aperte F6 e exporte em STL. Para exportar tudo de uma vez no Windows, rode `export_stl.bat`.
4. Se mudar alguma medida, edite `cad/params.py` e rode `python cad/build.py` (precisa só de Python com numpy).

## Antes de imprimir: meça e ajuste

Estas medidas vieram de fichas técnicas ou de estimativa. Com o paquímetro na peça real, corrija em `params.py`:

- [ ] Servo STS3215: corpo (45,2 × 24,7 × 35 mm), distância do eixo até a ponta (`SV_SHAFT_END`), diâmetro e espessura do horn, círculo dos 4 furos do horn.
- [ ] Microservo MG90S: corpo, largura com orelhas, altura das orelhas, posição do eixo, altura do eixo mais horn.
- [ ] Rolamento lazy susan de 4": tamanho, espessura, furo central e posição dos furos (as peças usam rasgos para tolerar diferenças).
- [ ] Diâmetro da cavilha ou tubo do mastro (3/4" = 19,05 mm).
- [ ] Imprima `fit_coupon` primeiro em cada máquina e anote qual furo encaixou melhor (insertos M3, pinos, guias M2,5, mastro e o anel do servo).

## Peças

| Peça | Qtd | Processo | Material |
| --- | --- | --- | --- |
| base_plate | 1 | Corte a laser | Acrílico preto 1/4" |
| base_lid | 1 | Corte a laser | Acrílico laranja 1/4" |
| base_shell | 1 | FDM | PETG preto |
| turret | 1 | FDM | PETG preto |
| servo_cap | 3 | FDM | PETG preto |
| upper_arm, forearm | 1 cada | FDM | PETG preto |
| upper_cover, fore_cover | 1 cada | FDM | PETG preto |
| upper_armor, fore_armor | 2 cada | FDM | PETG laranja |
| palm | 1 | FDM | PETG preto |
| palm_lid | 1 | FDM | PETG laranja |
| finger_proximal, finger_distal | 3 cada | Resina | Resina resistente preta |
| finger_pad | 3 | FDM | TPU 95A laranja |
| spool | 3 | Resina ou FDM | Resina resistente ou PETG |
| mast_socket, camera_plate | 1 cada | FDM | PETG preto |
| mast_head | 1 | FDM | PETG laranja |
| fit_coupon | 1 | FDM | PETG |

Impressão FDM sugerida: PETG, 4 perímetros, 25% a 40% de preenchimento giroide, camada de 0,2 mm. Braço e antebraço deitados de lado (canal aberto para cima), tampa dos servos com o topo para baixo.

## Hardware que não é impresso

| Item | Qtd | Observação |
| --- | --- | --- |
| Servo Feetech STS3215 12 V | 4 | Giro, ombro, cotovelo, punho |
| Microservo MG90S | 3 | Um por dedo |
| Rolamento lazy susan de 4" | 1 | Entre a tampa e a torre |
| Mola de tração | 1 (+1 reserva) | ~60 mm livre, 0,3 a 0,4 N/mm, tensão inicial 4 a 6 N, segura até ~130 mm |
| Grampo C de 3" | 2 | Prende a cauda da placa na borda da mesa, com borracha |
| Insertos roscados M3 | ~20 | Torre, braço, antebraço, carcaça |
| Parafusos M3, M2,5 e M2 | sortimento | Horns, tampas, orelhas dos microservos |
| Pinos de aço de 2 mm (ou filamento 1,75) | 6 | Articulações dos dedos |
| Linha trançada 0,5 mm (Dyneema) | 2 m | Tendões |
| Elástico de 1 mm | 1 m | Retorno dos dedos |
| Cavilha de madeira ou tubo de 3/4", 450 mm | 1 | Mastro da câmera |
| Parafusos M4 com porca | 5 | Pé do mastro e articulação da câmera |
| Parafuso 1/4"-20 curto | 1 | Rosca de tripé da webcam |
| Botão de emergência 22 mm, NF | 1 | Na tampa |
| Conector DC de painel 5,5 × 2,1 mm | 1 | Entrada de 12 V |
| Fita VHB | 1 rolo | Placas laranja dos braços |

## Ordem de montagem

1. Carcaça da base: insertos M3 nos cantos (em cima e embaixo), Arduino UNO nos suportes, adaptador Waveshare, relé e conversor com fita.
2. Servo de giro no berço central, com o cabo saindo pelo rasgo de trás.
3. Tampa laranja, lazy susan e torre. Prenda o horn na torre por baixo; encaixe a torre no eixo e aperte o parafuso central pelo furo de acesso, com o bolso do ombro ainda vazio.
4. Servo do ombro no bolso da torre e tampa do servo. Repita para cotovelo (no braço) e punho (no antebraço).
5. Garfos: cada elo aparafusa nos dois horns do servo anterior.
6. Mão: 3 microservos com carretéis, dedos com pinos, tendão do carretel até a ponta, elástico no dorso.
7. Mola: furo de baixo da barra da torre até o furo de 100 mm do braço. Ajuste trocando de furo.
8. Placa de base presa com 2 grampos na borda da mesa; mastro e câmera.
