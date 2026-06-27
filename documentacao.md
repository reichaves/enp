Esta documentação detalha o funcionamento, a lógica interna e os mecanismos de segurança dos scripts de cruzamento e auditoria desenvolvidos para o projeto "Escravo, nem pensar!".

Documentação Técnica: Sistema de Cruzamento de Dados (v7)
Este ecossistema de scripts foi projetado para correlacionar dados de trabalhadores resgatados de três fontes distintas: Perfil do Seguro-Desemprego, Radar SIT (dados oficiais da fiscalização) e Planilha Manual de Autos.

1. Script Principal: cruzamento_todos_anos.py
O script realiza o processamento em duas etapas principais, utilizando técnicas de limpeza, lógica nebulosa (fuzzy match) e blindagem de junção.

Pré-processamento e Limpeza
Normalização de Texto: Remove acentos, padroniza maiúsculas e elimina espaços duplos para evitar que variações de grafia (ex: "São" vs "Sao") impeçam o cruzamento.

Tratamento de Documentos: Limpa símbolos de CPFs e CNPJs e garante que os zeros à esquerda sejam preservados (11 dígitos para CPF, 14 para CNPJ).

Neutralização do "Falso Zero": A função remove_leading_zeros impede que campos de operação vazios sejam convertidos em "0", o que causaria vínculos errôneos com registros administrativos genéricos do Radar SIT.

Etapa 1: Vínculo Trabalhador × Perfil (Seguro-Desemprego)
Cruzamento por Nome: Tenta primeiro o match exato de nomes; para os remanescentes, aplica o fuzzy match com um limite de similaridade (cutoff) de 90.

Desempate por Proximidade de Data: Se um nome comum possuir múltiplos registros (homônimos), o sistema vincula ao registro cuja "Data de Resgate" seja a mais próxima da "Data de Afastamento" informada no auto manual.

Sanitização Temporal: Filtra automaticamente e remove pares onde a diferença de datas é superior a 365 dias, reduzindo o risco de homonímia falsa.

Trava de Unicidade: Aplica uma deduplicação rigorosa na chave nome + ano + operacao para garantir que cada resgate manual tenha apenas uma linha de perfil associada.

Etapa 2: Vínculo Operação × Radar SIT
Trava Temporal Absoluta: O script exige obrigatoriamente que o ano relatorio seja idêntico ao Ano do Radar SIT para validar o vínculo.

Blindagem contra "Empty String Match": Para evitar que trabalhadores sem empresa cruzem com operações sem nome de fazenda, o script converte campos vazios em nulos reais (np.nan) e utiliza o comando .dropna() durante a junção.

Hierarquia de Busca: Tenta vincular sucessivamente por CNPJ + Ano, depois por Nome do Estabelecimento + Ano e, por fim, por Nome Empresarial/Proprietário + Ano.

Deduplicação de Saída: Utiliza concatenação vertical para garantir que registros sem correspondência no Radar SIT permaneçam na base final, mas sem poluir as colunas de dados oficiais.

2. Script de Auditoria: auditoria_cruzamento.py
Atua como um "corretor cético" que valida a integridade do arquivo de saída antes da publicação.

Módulos de Verificação:
Produto Cartesiano: Verifica se existem chaves manuais duplicadas, o que indicaria falha na lógica de deduplicação.

Anomalia de "Operação 0": Detecta se houve vazamento de vínculos com registros genéricos do Radar SIT.

Integridade Temporal: Garante que 100% dos cruzamentos respeitaram o mesmo ano fiscal entre as bases.

Filtros de Segurança: Valida se a barreira de 365 dias para homônimos foi respeitada.

Status de Confiabilidade: Resume a classificação da coluna flag_estabelecimento, identificando casos que exigem revisão manual (status AUSENTE).

3. Guia para Alterações e Melhorias Futuras
Como adicionar novas colunas
No script de cruzamento, adicione o nome da coluna nas listas de cores (green_columns, blue_columns ou yellow_columns) para manter o padrão visual.

Certifique-se de que a nova coluna seja carregada como str no read_excel inicial para evitar erros de tipagem.

Ajuste de Rigidez no Cruzamento
Para ser mais flexível com nomes de fazendas, reduza o valor de overlap na função valida_estab (atualmente em 0.35).

Para ser mais rigoroso com homônimos, reduza o limite de diferenca_dias_resgate (atualmente em 365 dias).

Manutenção em 2026+
Quando os dados de 2025 do Radar SIT forem publicados, os casos atualmente marcados como SEM_CORRESPONDENCIA_SIT serão automaticamente processados pelo script sem necessidade de alteração no código, desde que os arquivos de origem sejam atualizados na pasta de dados.