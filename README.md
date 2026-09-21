
# Candidatas SP 2026 — MVP

Protótipo de plataforma informativa para organizar candidaturas femininas
a deputada federal e deputada estadual em São Paulo, combinando dados oficiais
do TSE com curadoria editorial documentada.

## 1. Instalação

```bash
pip install -r requirements.txt
```

## 2. Atualizar dados do TSE

```bash
python scripts/atualizar_tse.py
```

O script consulta o catálogo CKAN do Portal de Dados Abertos do TSE,
localiza o conjunto de candidaturas de 2026 e produz `data/candidatas_base.csv`.

## 3. Curadoria

Preencha na planilha CSV somente os campos editoriais:

- `regiao_atuacao`
- `resumo_trajetoria`
- `trajetoria_declarada`
- `atuacao_documentada`
- `pautas`
- `fonte_principal`
- `fonte_2`
- `fonte_3`
- `ultima_revisao_editorial`

Separe várias pautas com `|`.

Exemplo:

`Direitos das mulheres|Meio ambiente e clima|Educação`

## 4. Executar

```bash
streamlit run app.py
```

## 5. Princípios editoriais

- dados eleitorais vêm do TSE;
- cada informação biográfica ou temática deve ter fonte;
- distinguir trajetória declarada de atuação documentada;
- não criar ranking, nota ou recomendação de voto;
- tornar público o critério de inclusão partidária;
- registrar data da última revisão.

## Próximas etapas

1. Integrar automaticamente as fotos oficiais do TSE.
2. Integrar redes sociais oficiais.
3. Criar página individual por candidata.
4. Criar painel de curadoria.
5. Criar validação automática de links/fontes.
6. Melhorar SEO e compartilhamento em WhatsApp.
