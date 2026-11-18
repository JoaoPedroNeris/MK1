# Lotes de impressão do MK I v0.2c (18/11/2026, revisão 2)

Impressora: **Prusa MK3S+** (mesa 250 × 210 × 210 mm), bico 0,4, **PETG**. TPU das pontas em outra máquina.

**Resumo:** 31 peças FDM em **5 mesas de PETG + 1 de TPU**, com **1 troca de filamento** (laranja → preto). Tempo de máquina estimado pelo PrusaSlicer: **~60 h 20 min** de PETG (era 65 h 55 min na 1ª versão). Filamento: **~55 g laranja + ~842 g preto** (≈ 897 g).

Na prática o MK3S costuma demorar uns 5 a 10% a mais do que a estimativa.

## Ordem

| Lote | Cor | Peças | Tempo | Filamento | Altura máx. |
| --- | --- | --- | --- | --- | --- |
| 1 | laranja | cupom de folgas + 2 `upper_armor` + 2 `fore_armor` | 2 h 52 min | 45 g | 10 mm |
| ⏸ | | **Pare aqui e teste o cupom** (`03_docs/cupom_teste_folgas.md`). Se algum valor mudar, eu gero os STL de novo e refaço os lotes 2 a 5. | | | |
| 2 | laranja | `disco_espiral` | 43 min | 10 g | 4 mm |
| — | | **Troca de filamento: laranja → preto** | | | |
| 3 | preto | `turret`, `garra_base`, `carcaca`, `placa_guia`, 3 `mordente` (100% de preenchimento), 1 `servo_cap` | 21 h 34 min | 337 g | 95,5 mm |
| 4 | preto | `base_shell`, 2 `servo_cap`, 7 `presilha_cabo` | 18 h 23 min | 273 g | 55 mm |
| 5 | preto | `upper_arm`, `forearm`, `upper_cover`, `fore_cover` | 16 h 50 min | 232 g | 48 mm |
| 6 | TPU 95A | 3 `ponta_TPU` (outra máquina: Bambu ou CORE ONE) | poucos min | < 1 g | 1,5 mm |

Por que essa ordem:
- **Lote 1 primeiro e com as placas laranja.** As placas (`*_armor`) não têm furo nenhum (colam com fita VHB), então não dependem da folga e podem sair junto com o cupom. Imprimir o cupom em laranja não muda o teste e economiza uma troca de filamento.
- **Lote 2 logo depois do cupom aprovado**, enquanto a máquina ainda está com laranja. O disco tem furos passantes e o rasgo da espiral, então espera o cupom.
- **Lotes 3 → 4 → 5** seguem o checklist de montagem: garra, depois base e giro, depois braço.
- Três mesas pretas é o mínimo: `base_shell` (180 × 160) e `turret` (132 × 132) não cabem juntas, e o braço + antebraço (205 e 195 mm de comprimento) ocupam uma mesa inteira.

## Arquivos

| Arquivo | O que é |
| --- | --- |
| `loteN_*.3mf` | Projeto do PrusaSlicer com as peças já orientadas e posicionadas, perfil e ajustes por peça embutidos. Abra, confira e fatie. |
| `loteN_*.gcode` | Já fatiado (PrusaSlicer 2.7.2, perfil MK3S/MK3S+, 0,20 mm SPEED, Prusament PETG). Pode ir direto para o cartão SD. Começa com checagem de modelo e de bico (`M862`). |
| `loteN_*.png` | Vista de cima da mesa, para conferir. |
| `lote6_TPU_pontas_outra_maquina.3mf` | Só a geometria (3 pontas deitadas). Fatie no Bambu Studio ou PrusaSlicer com o perfil de TPU da máquina. |

Se o laboratório usar uma versão mais nova do PrusaSlicer, abra o `.3mf` e fatie de novo (ele vai aceitar os ajustes). Se aparecer "presets modificados", mantenha os do projeto.

## Ajustes usados

- Perfil base: **0,20 mm SPEED @MK3**, filamento **Prusament PETG** (240/250 °C, mesa 85/90 °C).
- **4 perímetros, 25% giroide, 5 camadas de topo e 4 de fundo** (dentro da recomendação 4 perímetros e 25 a 40% do README).
- **Preenchimento combinado a cada 2 camadas** (`infill_every_layers = 2`): o enchimento esparso sai em 0,4 mm, paredes e topos continuam em 0,2 mm. Não mexe em furo nem em encaixe. Corta ~10% no lote 3.
- O SPEED ficou cerca de 30% mais rápido que o QUALITY nas peças grandes (torre: 14 h 22 min contra 21 h 15 min), com o mesmo filamento. O fluxo fica limitado em 8 mm³/s pelo perfil do PETG.
- **Suporte automático (50°), estilo justo (snug), só nas peças que precisam:** `turret`, `garra_base`, `upper_arm`, `forearm`, `base_shell`, `servo_cap`. As outras ficam sem suporte.
- **Mordentes com 100% de preenchimento** (ajuste por peça no 3MF).
- Espaço entre peças: 6 mm, ou 9 a 12 mm perto de peça com suporte.
- **O cupom usa o mesmo perfil das peças.** Isso importa: o tamanho do furo depende do perfil. Se mudar o perfil depois, o resultado do cupom pode não valer.

## Orientação de cada peça (testei as 6 faces no fatiador)

| Peça | Como fica na mesa | Por quê |
| --- | --- | --- |
| `upper_arm`, `forearm` | Como modelado (Z para cima, garfo e bolso de pé) | Camadas ao longo do comprimento, que é por onde passa a flexão. Deitado de lado gastava mais que o dobro de suporte (82 g contra 37 g) e de pé fica com 205 mm de altura. O suporte segura a viga, que fica 7 mm acima da mesa por causa do disco do garfo. |
| `turret` | Como modelado (disco embaixo) | Menor tempo e suporte de forma razoável. Virada gasta 141 g de suporte. |
| `garra_base` | **De cabeça para baixo** (caixa do servo na mesa, garfos para cima) | 20 g de suporte contra 33 g e mais área na mesa (1060 mm² contra 21). |
| `base_shell` | Fundo na mesa | Virada gastaria 259 g de suporte. |
| `servo_cap` | Como modelado (frisos embaixo, nervuras em cima) | Só 2 g de suporte e as nervuras de estilo saem limpas. |
| `upper_cover`, `fore_cover`, `carcaca`, `placa_guia`, `disco_espiral`, cupom | Planas, como modeladas | Sem suporte. |
| `upper_armor`, `fore_armor` | Deitadas, **face de colar na mesa** | Sem suporte, face lisa para a fita VHB. |
| `mordente_1/2/3` | Deitados de lado | Os três são a mesma peça girada 120°. Deitado: 0,3 g de suporte e camadas ao longo do dedo (de pé ele quebraria na camada). |
| `presilha_cabo` | Face de apoio na mesa (como o README pede) | O túnel de 8 mm faz ponte sem suporte. |
| `ponta_TPU` | Deitada (1,5 mm de altura) | Mais estável em TPU. |

## Dicas para PETG no MK3S+

- Use a **chapa texturizada** se tiver; na lisa, passe cola bastão para o PETG não arrancar o PEI.
- O carretel preto precisa ter **pelo menos ~900 g** para os lotes 3 a 5. Se o carretel estiver no fim, comece o lote 3 (o maior, 357 g) num carretel novo.
- O lote 3 tem ~21,5 h. Se o laboratório não deixar uma impressão desse tamanho, separe em dois: só a `turret` (~13 h) e o resto da garra (~8,5 h).

## O que mudou na revisão 2

- **`servo_cap` corrigida (v0.2d).** Os frisos de baixo encostavam na tampa só numa linha, porque o chanfro de 1,5 mm comia a largura toda do friso. Agora o friso sobe 1,5 mm para dentro do corpo e a peça é um corpo só (antes eram 3). Medidas externas iguais. Mudança em `02_cad_fonte/cad/parts.py` (`servo_cap`), STL novo em `01_imprimir/02_braco/servo_cap_x3.stl`; o antigo foi para `99_arquivo`.
- **Mais rápido:** suporte justo + preenchimento combinado tiraram ~5,5 h e ~38 g, sem mudar perfil nem camada.
- **Encaixe nas mesas:** as 3 mesas pretas já usam 57 a 66% da área (contando o contorno das peças), o resto é o espaço mínimo entre peças com suporte. Não dá para tirar uma mesa preta: base (180 × 160) e torre (132 × 132) não cabem juntas, e braço + antebraço (205 e 195 mm) enchem uma mesa. As mesas laranja ficam vazias de propósito, porque só cabe nelas o que não depende do cupom.
- Juntar mais peças numa mesa quase não reduz o tempo total: a máquina gasta o mesmo tempo por peça. O ganho por mesa a menos é só aquecer e nivelar (~5 a 10 min).

## Revisão 3 (18/11, 20h50)

- Lote 3 refeito com a `garra_base` nova (furo central do horn 9 → 6,5 mm, `01_imprimir/03_garra/garra_base.stl`). Mesma orientação e posição. Tempo 21 h 34 min e 337 g, praticamente iguais (+0,2 g).

## Avaliação estrutural e funcional (18/11, 20h30)

| Mudança | Situação | Por quê |
| --- | --- | --- |
| Suporte justo (snug) | **Aplicada, não compromete** | Só muda o formato do suporte, que é arrancado depois. A peça é igual. |
| Preenchimento a cada 2 camadas | **Aplicada, não compromete** | Só o enchimento esparso (25%) sai em 0,4 mm, que é o máximo do bico 0,4. Os 4 perímetros, os topos e fundos e os mordentes (100%) continuam em 0,2 mm. A carga passa pelos perímetros e as medidas e furos não mudam. |
| Frisos da servo_cap (v0.2d) | **Aplicada, melhora** | O friso que estava solto agora é colado na tampa. Medidas externas e de encaixe iguais. |
| Camada 0,30 mm | **Rejeitada** | Os furos do horn nos garfos ficam deitados na impressão, e com 0,30 mm eles saem mais escalonados. O cupom só testa furos de pé, então não pega isso. As alturas do bolso do servo também ficariam arredondadas em degraus de 0,30 mm. Risco de folga no horn e no servo. |
| Disco espiral junto com o cupom | **Rejeitada** | O rasgo da espiral e os furos passantes dependem do resultado do cupom. Economizaria só ~43 min. |

## Filamento por mesa

| Lote | Cor | Gramas |
| --- | --- | --- |
| 1 | laranja | 45 g |
| 2 | laranja | 10 g |
| 3 | preto | 337 g |
| 4 | preto | 273 g |
| 5 | preto | 232 g |
| 6 | TPU | < 1 g |
| **Total PETG** | | **897 g** (55 g laranja + 842 g preto) |

Valores do PrusaSlicer, incluindo saia, linha de purga e suportes. Para o pedido ao supervisor, some uns 10% de margem para falha ou reimpressão: **~990 g, ou seja, 1 kg**.

## Opções avaliadas e não aplicadas

- **Camada 0,30 mm (perfil 0.30mm DRAFT):** lote 3 cai de ~21,5 h para ~19,5 h e o lote 5 de ~17 h para ~15 h (cerca de −15%), mas gasta ~10% mais filamento e o acabamento fica mais grosso. Se usar, o cupom tem que sair com o mesmo perfil.
- **Juntar o disco no lote 1:** economiza uma mesa (~43 min + aquecimento). O risco é que o disco tem furos passantes e o rasgo da espiral; se o cupom mudar o valor do passante, ele tem que ser reimpresso (10 g).
- **3 perímetros:** ~4% mais rápido, mas sai da recomendação de 4 perímetros nas peças de carga.
