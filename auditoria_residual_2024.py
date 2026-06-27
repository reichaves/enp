import os
import pandas as pd
import re

# Definição dos Caminhos
path_dados = r"E:\Code\enp\dados_2024_2025"
path_resultados = r"E:\Code\enp\scripts\resultados_scripts"

arquivo_final = os.path.join(path_resultados, "cruzamento_final_todos_anos_maio_2026_v9.xlsx")
arquivo_radar = os.path.join(path_dados, "ENP - Trabalho escravo por local e atividade(2).xlsx")
arquivo_saida = os.path.join(path_resultados, "relatorio_auditoria_residual_2024.xlsx")

def remove_leading_zeros(num_str):
    if pd.isna(num_str) or str(num_str).strip() in ('', 'nan', 'NaN'): return ''
    val = str(num_str).strip()
    if val == '0': return '0'
    val = val.lstrip('0')
    return val if val else '0'

def limpar_documento(doc):
    if pd.isna(doc): return ''
    doc_str = str(doc).strip()
    return re.sub(r'[\.\-\/]', '', doc_str)

print("Carregando base de resultados V9...")
try:
    df_final = pd.read_excel(arquivo_final, sheet_name='Resultados', dtype=str)
except FileNotFoundError:
    print(f"[ERRO] Arquivo não encontrado: {arquivo_final}")
    exit()

print("Carregando base bruta do Radar SIT...")
df_radar = pd.read_excel(arquivo_radar, sheet_name='Dados', dtype=str)

# 1. Isolar os alvos da auditoria
df_alvo = df_final[
    (df_final['ano relatorio'] == '2024') & 
    (df_final['flag_estabelecimento'] == 'SEM_CORRESPONDENCIA_SIT')
].copy()

if df_alvo.empty:
    print("Nenhum caso 'SEM_CORRESPONDENCIA_SIT' encontrado para 2024. Nada a auditar.")
    exit()

print(f"Total de trabalhadores isolados para auditoria (2024): {len(df_alvo)}")

# ---> CORREÇÃO AQUI <---
# Removemos as colunas azuis do Radar SIT que já existem na planilha final,
# para evitar que o Pandas crie sufixos (_x e _y) durante o merge.
colunas_conflito = ['Ano', 'Proprierário', 'Estabelecimento Inspecionado', 'Município', 'UF']
df_alvo = df_alvo.drop(columns=[c for c in colunas_conflito if c in df_alvo.columns])

# 2. Preparar Radar SIT para o cruzamento por número de operação
df_radar['Ano'] = df_radar['Ano'].astype(str).str.strip()
df_radar['Operação_Limpa'] = df_radar['Operação'].apply(remove_leading_zeros)
df_radar['CNPJ_Radar_Limpo'] = df_radar['CNPJ-CEI-CPF'].apply(limpar_documento).apply(lambda x: x.zfill(14) if len(x) > 11 else x.zfill(11))

# Remover duplicatas do Radar SIT
colunas_radar_uteis = ['Ano', 'Operação_Limpa', 'CNPJ_Radar_Limpo', 'Proprierário', 'Estabelecimento Inspecionado', 'Município', 'UF']
df_radar_dedup = df_radar[colunas_radar_uteis].drop_duplicates(subset=['Ano', 'Operação_Limpa'], keep='first')

# 3. Cruzar Base Alvo com Radar SIT usando apenas Ano e Operação
df_alvo['operacao_limpa'] = df_alvo['operacao'].apply(remove_leading_zeros)

resultado_auditoria = pd.merge(
    df_alvo, 
    df_radar_dedup, 
    left_on=['ano relatorio', 'operacao_limpa'], 
    right_on=['Ano', 'Operação_Limpa'], 
    how='left'
)

# 4. Criar diagnóstico de CNPJ
def diagnosticar_cnpj(row):
    cnpj_sd = str(row.get('cpf_cnpj_empregador_str', '')).strip()
    cnpj_radar = str(row.get('CNPJ_Radar_Limpo', '')).strip()
    
    if cnpj_sd == 'nan' or not cnpj_sd: cnpj_sd = ''
    if cnpj_radar == 'nan' or not cnpj_radar: cnpj_radar = ''
    
    if not cnpj_radar:
        return "OPERAÇÃO NÃO ENCONTRADA NO RADAR SIT"
    if not cnpj_sd:
        return "TRABALHADOR SEM CNPJ NO SEGURO-DESEMPREGO"
    if cnpj_sd == cnpj_radar:
        return "IGUAIS (Anomalia de nome/vazio na V9)"
    return "DIVERGENTE (Erro de digitação/Matriz x Filial)"

resultado_auditoria['DIAGNOSTICO_CNPJ'] = resultado_auditoria.apply(diagnosticar_cnpj, axis=1)

# 5. Organizar colunas para leitura humana
colunas_finais = [
    'ano relatorio',
    'operacao',
    'nome_trabalhador_limpo',
    'estabelecimento_inspecionado_limpo',
    'cpf_cnpj_empregador_str',
    'DIAGNOSTICO_CNPJ',
    'CNPJ_Radar_Limpo',
    'Proprierário',
    'Estabelecimento Inspecionado',
    'Município',
    'UF'
]

relatorio_final = resultado_auditoria[colunas_finais].copy()
relatorio_final = relatorio_final.sort_values(by=['operacao', 'nome_trabalhador_limpo'])

# 6. Exportar
relatorio_final.to_excel(arquivo_saida, index=False)
print(f"Relatório gerado com sucesso: {arquivo_saida}")
print("A equipe de checagem deve focar na coluna 'DIAGNOSTICO_CNPJ' para atestar as discrepâncias.")