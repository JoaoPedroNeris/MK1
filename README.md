# Stark Desk MK I — pasta do projeto (v0.2c)

Organizada em 18/11/2026. Nada foi apagado: o que saiu do caminho está em `99_arquivo/`, e o arquivo `MAPA_movimentacao.md` diz de onde veio cada coisa.

**Regra de ouro:** para imprimir ou montar, use **só** `01_imprimir/`. Se um STL não está lá, ele não é para imprimir.

## Estrutura

| Pasta | O que tem | Quando usar |
| --- | --- | --- |
| `01_imprimir/` | Só os STL finais e atuais, separados por subconjunto. O sufixo `_x3`, `_x7`, `_x2` no nome é a quantidade a imprimir. | Na hora de fatiar e imprimir. |
| `02_cad_fonte/cad/` | Código paramétrico do braço (`params.py` com todas as medidas, `parts.py`, `assembly.py`, `exportar_stl.py`). | Para mudar uma medida e gerar STL de novo. |
| `02_cad_fonte/fusion_scripts/` | Scripts do Fusion: garra, cupom de teste, importar montagem. Já apontam para as pastas novas. | Para mexer na garra ou no cupom no Fusion. |
| `03_docs/` | Cupom de teste, passa-cabos, mudanças da v0.2c, auditorias de carga e de paredes. | Para consultar durante a montagem. |
| `04_imagens/` | Imagens atuais (montagem v0.2b, garra, eletrônica na base, cabos, corte do bolso). | Referência visual. |
| `05_visualizacao_fusion/montagem_b/` | Malhas da montagem inteira posicionadas (inclui servos, eletrônica, lazy susan). **Não são para imprimir.** | Abrir no Fusion com `importar_montagem_v02.py` para ver como tudo encaixa. |
| `99_arquivo/` | v0.1, backup antes da correção de paredes, STL obsoletos, montagem antiga com mastro e mola, imagens antigas. | Só se precisar recuperar algo. Não imprima nada daqui. |

## O que imprimir

Total: 32 peças FDM (31 do braço e garra, mais o cupom), mais 2 chapas de acrílico no laser. Todas cabem na mesa de 220 × 220 mm. Sugestão: PETG, 4 perímetros, 25 a 40% giroide, camada 0,2 mm.

| Ordem | Arquivo (`01_imprimir/…`) | Qtd | Material | Versão |
| --- | --- | --- | --- | --- |
| 1 | `00_teste_primeiro/fit_coupon_v02b.stl` | 1 | PETG | v0.2b |
| 2 | `01_base/base_shell.stl` | 1 | PETG preto | v0.2c + janela USB maior (19/11) |
| 2 | `01_base/turret.stl` | 1 | PETG preto | v0.2c (já com bloco da presilha do ombro) |
| 3 | `02_braco/upper_arm.stl` | 1 | PETG preto | v0.2c |
| 3 | `02_braco/forearm.stl` | 1 | PETG preto | v0.2c |
| 3 | `02_braco/servo_cap_x4.stl` | **4** | PETG preto | v0.2d (2 no ombro, cotovelo, punho; até 18/11 estava x3 por engano) |
| 3 | `02_braco/upper_cover.stl` | 1 | PETG preto | v0.2c (já com saída do cabo) |
| 3 | `02_braco/fore_cover.stl` | 1 | PETG preto | v0.2c (já com saída do cabo) |
| 3 | `02_braco/upper_armor_x2.stl` | **2** | PETG laranja | v0.2c (exportado em 18/11; é simétrico, as 2 são iguais) |
| 3 | `02_braco/fore_armor_x2.stl` | **2** | PETG laranja | v0.2c (idem) |
| 4 | `03_garra/garra_base.stl` | 1 | PETG preto | v0.2b + inserto da presilha do punho |
| 4 | `03_garra/carcaca.stl` | 1 | PETG preto | v0.2b |
| 4 | `03_garra/disco_espiral.stl` | 1 | PETG laranja | v0.2b |
| 4 | `03_garra/placa_guia.stl` | 1 | PETG preto | v0.2b |
| 4 | `03_garra/mordente_1/2/3.stl` | 1 de cada | PETG preto, 100% de preenchimento | v0.2b |
| 4 | `03_garra/ponta_TPU_1/2/3.stl` | 1 de cada | TPU 95A | v0.2b |
| 5 | `04_cabos/presilha_cabo_x7.stl` | **7** | PETG preto (face de apoio na mesa) | v0.2b |

Não impresso em FDM:
- **Tampa da base (acrílico laranja 6 mm) e placa de base (acrílico preto 6 mm), no laser:** `01_imprimir/05_laser_acrilico/` tem SVG e DXF da v0.2 (tampa com furo de 62 mm, coluna do e-stop em (82,8; −36), placa sem furo do mastro). Vermelho/camada CORTAR = cortar; preto/camada GRAVAR = gravar. Unidades em mm (tampa 180 × 160, placa 255 × 160). Prévia em `04_imagens/laser_v02_previa.png`. Gerados por `02_cad_fonte/cad/exportar_laser.py`.
- Servos (6× STS3215), horns, lazy susan, e-stop, eletrônica: compra. As malhas deles em `05_visualizacao_fusion` são só referência.

## Ordem de uso

1. **Imprima só o cupom** (`00_teste_primeiro`) e siga `03_docs/cupom_teste_folgas.md`. Me mande os números vencedores (inserto, passante, piloto, servo). Se algum for diferente do valor atual, eu ajusto `params.py` e gero os STL de novo antes de você imprimir o resto.
2. Imprima a **base** e a **torre** (`01_base`).
3. Imprima o **braço** (`02_braco`): braço, antebraço, 4 tampas de servo, 2 tampas de baixo, 4 placas laranja.
4. Imprima a **garra** (`03_garra`).
5. Imprima as **7 presilhas** (`04_cabos`) e monte os cabos seguindo `03_docs/passa_cabos.md`.
6. Para montar, siga o checklist por fases do documento de consolidação: https://claude.ai/artifact/RtfCenxk7A3U9dGUWAr5vJ. Os parafusos de cada encaixe estão em `03_docs/mapa_parafusos_v02c.md`.

## Documentos (`03_docs/`)

| Arquivo | Para que serve |
| --- | --- |
| `cupom_teste_folgas.md` | Ordem dos 9 furos do cupom e o que testar em cada um (sem paquímetro). |
| `passa_cabos.md` | Onde vão as presilhas, parafusos (4× M3×14, 2× M3×12) e como testar o laço de cada junta. |
| `mapa_parafusos_v02c.md` | Parafuso certo de cada encaixe e o total para comprar (39 M3×8, 4 M3×10, 25 M3×12, 4 M3×14, 4 M3×6, 32 insertos). |
| `mudancas_v02c_paredes.md` | O que mudou na v0.2c (paredes dos insertos, furos do horn de 6,5 mm). |
| `eletronica_lista_compra.md` | Lista de compra da eletrônica (servos, fonte, e-stop, cabos), com quantidade, especificação e preço aproximado (19/11). |
| `eletronica_auditoria.md` | Auditoria da eletrônica: correntes, fonte e fusível, diagrama de ligação, encaixe na base, riscos e próximos passos (19/11). |
| `auditoria/` | Scripts e resultados das contas de carga, torque, insertos e paredes. Os da subpasta `paredes_cargas_18nov` são registro (usam caminhos da nuvem). |

## Se precisar gerar STL de novo

- Braço, torre, base, tampas: edite `02_cad_fonte/cad/params.py` e rode `python 02_cad_fonte/cad/exportar_stl.py <pasta_saida>` (precisa de `pip install numpy manifold3d trimesh`). Ele gera com os nomes sem sufixo (`servo_cap.stl`): renomeie para `_x3` ao copiar para `01_imprimir`.
- Acrílico da base (laser): `python 02_cad_fonte/cad/exportar_laser.py <pasta_saida>` (DXF precisa de `pip install ezdxf`).
- Garra e cupom: scripts em `02_cad_fonte/fusion_scripts/`, rodados dentro do Fusion. Eles já salvam direto em `01_imprimir/03_garra` e `01_imprimir/00_teste_primeiro`.
- Montagem visual: `02_cad_fonte/cad/montagem_v02.py` grava em `05_visualizacao_fusion/montagem_b`, e `importar_montagem_v02.py` abre no Fusion.

## Versões e Git

- `main` tem sempre a versão atual. Cada versão fechada ganha uma **tag** (`v0.2c`, depois `v0.3`...) e uma linha em `CHANGELOG.md`.
- Ao lançar versão nova: gere os STL, substitua os de `01_imprimir/` (o Git guarda os antigos no histórico, então não precisa mais copiar para `99_arquivo/`), atualize o `CHANGELOG.md`, faça o commit e crie a tag.
- **Fora do repositório** (`.gitignore`): malhas de `05_visualizacao_fusion/` (~45 MB, regeráveis), a montagem antiga com mastro em `99_arquivo/`, os `.gcode` (gerados a partir dos `.3mf`) e `__pycache__`.

## Decisões em vigor (resumo)

Tudo em parafuso M3. Ombro com 2 STS3215 lado a lado, sem mola (6 servos no total: giro, 2 no ombro, cotovelo, punho, garra). Sem mastro de webcam. Garra de 3 pontas com disco espiral, abertura Ø30. Carga útil recomendada 150 g. Cotovelo limitado a −105° por causa das presilhas.

## Erros: o que está resolvido e o que depende de você (18/11, 21h)

Resolvidos no modelo e nos arquivos: paredes dos insertos, furos do horn no garfo do ombro, furo de 6,5 mm nos garfos, na torre e na `garra_base`, rasgo do cabo, coluna da tampa, cupom só M3, limite do cotovelo, frisos da `servo_cap` (v0.2d), armaduras laranja com STL, **arquivo de corte a laser da v0.2**, **mapa de parafusos e lista de compra** (incluindo o parafuso da frente da tampa do servo, que agora é M3×10) e **a 4ª tampa de servo que faltava** (lote 4 já refatiado com 3 `servo_cap`; com a do lote 3 dá 4). As orelhas da carcaça da garra ficam em 9 mm de propósito.

Dependem de você ou do hardware:
- **Medidas com o servo na mão** (fim do eixo, horn, rosca, massa, furos do lazy susan, comprimento do cabo) e **tamanho real dos módulos eletrônicos**: teste por encaixe e régua, fases 1 e 2 do checklist.
- **Pino Ø3 do mordente:** só o teste diz se aguenta; plano B é parafuso M3 como pino.
- **Backup:** a pasta já está no GitHub (JoaoPedroNeris/MK1); falta salvar os documentos do Fusion.
- **Conversor 12→5 V:** perdeu a função (alimentava os dedos). Recomendo não usar e alimentar o relé pelos 5 V do Arduino; a decisão é sua.
- **Riscos de montagem e software** (IDs dos servos, ombro duplo brigando, queda no e-stop, pulo ao religar): resolvem-se na configuração dos servos e no software, não no modelo. Estão no documento de consolidação, seção 3.
