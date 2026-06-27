# Regras do Projeto (ENP - Escravo, Nem Pensar!)

Este arquivo documenta as diretrizes e especificações do repositório para futuros agentes ou ferramentas integradas.

## 1. Estrutura do Repositório e Versionamento
* A branch padrão é **`main`**. Não devem ser criadas ou enviadas alterações para a antiga branch `master`.
* Os seguintes diretórios são restritos e estão configurados no `.gitignore`, não devendo nunca ser adicionados ao controle de versão:
  * `dados_2024_2025/` (dados brutos contendo PII)
  * `backup/` (cópias locais e backups temporários)
  * `resultados_scripts/` (planilhas consolidadas geradas pelo script)

## 2. Documentação Técnica
* A versão atual e válida dos algoritmos de cruzamento e auditoria de dados é a **v11**.
* Qualquer atualização na lógica de processamento dos scripts deve ser replicada de forma sincronizada em ambos os arquivos de documentação técnica:
  * No arquivo Markdown: [documentacao.md](file:///E:/code/enp/documentacao.md)
  * No arquivo Microsoft Word: [Documentação Técnica - Lógica de Processamento (v11).docx](file:///E:/code/enp/Documentação%20Técnica%20-%20Lógica%20de%20Processamento%20(v11).docx)
* O arquivo `.docx` deve ser manipulado em ambiente Python utilizando a biblioteca `python-docx` para preservar a estrutura de estilos.

## 3. Diretrizes de ETL e Scripts
* O processamento principal é composto por:
  * [cruzamento_todos_anos.py](file:///E:/code/enp/cruzamento_todos_anos.py): Script primário de ETL (Extract, Transform, Load).
  * [auditoria_cruzamento.py](file:///E:/code/enp/auditoria_cruzamento.py): Script validador pós-processamento de integridade e consistência.
  * [auditoria_residual_2024.py](file:///E:/code/enp/auditoria_residual_2024.py): Script de diagnóstico focado em registros residuais de 2024.
* No desenvolvimento de novas funcionalidades, manter a regra de conformidade visual do Excel final gerado via `openpyxl`:
  * Amarelo (`#FFF2CC`): Colunas nativas dos Autos Manuais.
  * Verde (`#E2EFDA`): Colunas do perfil do Seguro-Desemprego.
  * Azul (`#DDEBF7`): Colunas oficiais obtidas do Radar SIT.
