# 05_visualizacao_fusion (fora do Git)

As malhas da montagem completa (`montagem_b/`, ~45 MB) não vão para o repositório: são só para ver a montagem no Fusion, não para imprimir, e são geradas de novo a qualquer momento.

Para gerar:

```
pip install numpy manifold3d trimesh
python 02_cad_fonte/cad/montagem_v02.py
```

Depois abra no Fusion com `02_cad_fonte/fusion_scripts/importar_montagem_v02.py`.
