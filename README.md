# Sistema de Cruzamento e Auditoria de Dados — Projeto "Escravo, nem pensar!"

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Pandas](https://img.shields.io/badge/Pandas-v1.3%2B-darkblue.svg)
![OpenPyXL](https://img.shields.io/badge/OpenPyXL-v3.0%2B-orange.svg)
![Status](https://img.shields.io/badge/Status-Ativo-success.svg)

Este repositório contém o ecossistema de scripts em Python projetado para o tratamento, cruzamento (merge) e auditoria sistemática de dados de trabalhadores resgatados sob condições análogas à escravidão no Brasil. 

O objetivo do sistema é correlacionar informações provenientes de três bases de dados principais para consolidação e análise estruturada pela equipe do projeto **"Escravo, nem pensar!"**:
1. **Planilha Manual de Autos**: Registros históricos inseridos manualmente pela equipe da iniciativa.
2. **Perfil do Seguro-Desemprego**: Dados cadastrais e demográficos de trabalhadores que solicitaram o benefício após o resgate.
3. **Radar SIT**: Cadastro oficial de fiscalizações da Subsecretaria de Inspeção do Trabalho.

---

## Autor

* **Reinaldo Chaves** (reichaves@gmail.com)
  * GitHub: [@reichaves](https://github.com/reichaves)

---

## Estrutura do Repositório

* `.gitignore`: Configuração para ignorar arquivos locais, ambientes virtuais e pastas contendo dados sensíveis ou resultados volumosos.
* `cruzamento_todos_anos.py`: Script principal de limpeza, cruzamento estruturado e exportação formatada das bases.
* `auditoria_cruzamento.py`: Script validador pós-processamento, que audita a integridade física e temporal do arquivo final gerado.
* `auditoria_residual_2024.py`: Script focado na análise de dados que permaneceram sem correspondência com o Radar SIT no ano fiscal de 2024, efetuando o diagnóstico de CNPJs.
* `documentacao.md`: Documentação técnica descrevendo as especificações e a lógica de processamento detalhada de cada módulo.

> **Observação:** As pastas `dados_2024_2025/`, `backup/` e `resultados_scripts/` contêm dados brutos de identificação e arquivos finais de trabalho que estão sob restrição de acesso e foram excluídos do controle de versão via `.gitignore`.

---

## O que é ETL?

**ETL** é a sigla para **Extract, Transform, Load** (Extrair, Transformar e Carregar). Representa um fluxo estruturado de engenharia de dados para consolidação e integração de informações:

* **Extract (Extração):** Leitura das bases de dados brutas de entrada (`trabalhadores_mai22.xlsx`, `ENP - Perfil do resgatado no Brasil.xlsx` e `radarsit_mai22.xlsx`) no diretório `dados_2024_2025/`.
* **Transform (Transformação):** Higienização de strings, padronização de CPFs/CNPJs, resolução de homônimos por proximidade temporal, cruzamento fuzzy e junção hierárquica em [cruzamento_todos_anos.py](file:///E:/code/enp/cruzamento_todos_anos.py).
* **Load (Carregamento):** Gravação do resultado consolidado e formatado no arquivo final Excel dentro do subdiretório `resultados_scripts/`.

---

## Especificações Técnicas e Lógicas de ETL

### 1. Pré-processamento e Limpeza
* **Normalização de Textos:** Conversão automática de strings para caixa alta, remoção de caracteres acentuados (normalização Unicode NFKD) e eliminação de espaços duplicados ou marginais.
* **Validação de Documentos:** Limpeza de pontuação de CPFs e CNPJs e preenchimento com zeros à esquerda (*padding*), garantindo tamanho fixo de 11 caracteres para pessoas físicas e 14 para pessoas jurídicas.
* **Neutralização do "Falso Zero":** Conversão de valores vazios/indeterminados em campos de identificadores para nulos reais (`NaN`), impedindo que campos nulos cruzem com registros corrompidos ou genéricos.

### 2. Cruzamento Trabalhador × Perfil do Seguro-Desemprego
O script realiza o processamento em formato hierárquico:
* **Fase 1:** Correspondência exata pelo nome do trabalhador.
* **Fase 2:** Correspondência nebulosa (*fuzzy match* utilizando a distância Levenshtein com `fuzzywuzzy`) para casos remanescentes, com limite de similaridade ajustado em 90%.
* **Desempate de Homônimos:** Havendo múltiplos candidatos (nomes idênticos ou homônimos), o sistema associa ao registro cuja "Data de Resgate" seja mais próxima da "Data de Afastamento" declarada na planilha de autos manuais. Se a diferença exceder 365 dias, o par é marcado com a sinalização `flag_data_divergente = True`.
* **Validação de Sobrenomes:** Implementa uma trava que valida a existência de ao menos uma palavra em comum entre os sobrenomes (desconsiderando preposições), descartando falsos homônimos.

### 3. Cruzamento Operação × Radar SIT
A integração com o Radar SIT ocorre em três níveis de correspondência sob a restrição do mesmo ano fiscal do auto de infração:
1. **Nível 3 (Prioridade Máxima):** Correspondência exata por documento (CNPJ ou CPF do empregador).
2. **Nível 2:** Correspondência exata pelo nome limpo do estabelecimento inspecionado.
3. **Nível 1 (Mínimo):** Correspondência de nomes administrativos (proprietário ou razão social).

Os dados que não encontram par no Radar SIT não são excluídos do relatório final (mantendo-se via junção externa parcial), mas são classificados sob a flag `flag_estabelecimento = SEM_CORRESPONDENCIA_SIT`.

---

## Execução e Auditorias

### Dependências Requeridas
* Python $\ge$ 3.8
* pandas
* openpyxl
* fuzzywuzzy
* python-Levenshtein
* matplotlib
* seaborn
* plotly

### Execução dos Módulos

1. **Instalar dependências:**
   ```bash
   pip install pandas openpyxl fuzzywuzzy python-Levenshtein matplotlib seaborn plotly
   ```

2. **Processar o cruzamento completo:**
   ```bash
   python cruzamento_todos_anos.py
   ```

3. **Auditar a base gerada:**
   ```bash
   python auditoria_cruzamento.py
   ```

4. **Gerar relatório de resíduos (Casos de 2024):**
   ```bash
   python auditoria_residual_2024.py
   ```

O script `auditoria_cruzamento.py` executará 6 testes estruturais de validação:
* **Produto Cartesiano:** Detecta se a deduplicação de chaves falhou e se existem registros duplicados de trabalhadores associados à mesma operação.
* **Auditoria de Homônimos:** Exibe contagens de registros únicos e fator de reincidência.
* **Anomalia "Operação 0":** Alerta sobre falsos positivos vinculados ao registro padrão "0" do Radar SIT.
* **Validação Temporal:** Garante que a restrição de 365 dias de diferença temporal não foi violada.
* **Integridade do Ano Fiscal:** Garante que dados de anos fiscais divergentes não sofreram *merge* acidental.
* **Confiabilidade:** Resume o status de consistência dos estabelecimentos cruzados (`VALIDADO_POR_CNPJ`, `COMPATIVEL`, `DIVERGENTE`, `AUSENTE`).
