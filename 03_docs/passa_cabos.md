# Passa-cabos v0.2b (opção A: laço à mostra + presilhas M3), 18/11

Todos os laços ficam do lado **+Y** do braço (o mesmo lado em todas as juntas).

## O que imprimir (STL em `v0.2/stl/cabos/`)
| Peça | Qtd | O que mudou |
| --- | --- | --- |
| presilha_cabo.stl | 7 | Nova. Túnel 8 × 3 mm com friso de aperto. Imprimir com a face de apoio na mesa. |
| upper_cover.stl, fore_cover.stl | 1 cada | Saída do cabo aberta para a borda +Y nas duas pontas. |
| turret.stl | 1 | Bloco atrás do pedestal com 1 inserto M3 para a presilha do ombro. |
| garra_base.stl | 1 | 1 inserto M3 na face de fora da caixa do servo (lado +Y) para a presilha do punho. |

Braço e antebraço **não mudam**: as presilhas das tampas usam os mesmos insertos da tampa de baixo.

## Parafusos
- 4 × M3 × 14 nas tampas de baixo (no lugar dos parafusos curtos), cada um prendendo 1 presilha.
- 2 × M3 × 10 com inserto novo: torre e garra.
- Sobra 1 presilha de reserva.

## Montagem
1. Passe o cabo por dentro do canal do braço, como antes.
2. Em cada ponta, tire o cabo pela saída da tampa, passe por baixo da presilha e aperte.
3. Entre as duas presilhas de cada junta deixe ~5 cm de folga (parâmetro `LACO`) e mova a junta até o fim nos dois sentidos para ver se o laço não estica nem enrosca.
4. Base: o cabo desce pelo furo da torre e faz um laço solto dentro da caixa. Limite o giro da base a ±135° no software (`YAW_LIM`).

## Teste de encaixe sem paquímetro
Se o cabo não entrar no túnel ou ficar solto, mude `CABO_L` / `CABO_A` (no Fusion: MK1_presilha_cabo_v02, ou em `cad/params.py`) e reimprima só uma presilha.

## Interferências conferidas (varredura de 2,5°)
- Ombro: −27,5° a +115° (igual a antes).
- Punho: −115° a +112,5° (igual a antes).
- Cotovelo: dobra máxima caiu de −117,5° para −105°, porque as duas presilhas do cotovelo se encostam. A pose padrão (−82°) não é afetada.
