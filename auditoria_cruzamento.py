import pandas as pd
import os

def auditar_base(caminho_arquivo):
    print(f"--- INICIANDO AUDITORIA: {os.path.basename(caminho_arquivo)} ---")
    
    try:
        if caminho_arquivo.endswith('.csv'):
            df = pd.read_csv(caminho_arquivo, dtype=str)
        else:
            df = pd.read_excel(caminho_arquivo, sheet_name='Resultados', dtype=str)
    except Exception as e:
        print(f"[ERRO FATAL] Falha ao ler o arquivo: {e}")
        return

    print("\n1. AUDITORIA DE PRODUTO CARTESIANO (Duplicação Estrutural)")
    if all(c in df.columns for c in ['nome_trabalhador_limpo', 'ano relatorio', 'operacao']):
        df['chave_manual'] = df['nome_trabalhador_limpo'].fillna('') + "|" + df['ano relatorio'].fillna('') + "|" + df['operacao'].fillna('')
        n_duplicados = df.duplicated(subset=['chave_manual'], keep='first').sum()
        if n_duplicados > 0:
            print(f"[FALHA] Detectados {n_duplicados} registros gerados por falha de deduplicação.")
        else:
            print("[OK] Zero duplicatas atreladas à mesma chave primária manual.")

    print("\n2. AUDITORIA DE HOMÔNIMOS E REINCIDENTES")
    if 'nome_trabalhador_limpo' in df.columns:
        n_total = len(df)
        n_unicos = df['nome_trabalhador_limpo'].nunique()
        print(f"- Linhas totais: {n_total}")
        print(f"- Trabalhadores únicos: {n_unicos}")
        print(f"- Fator de reincidência/homonímia: {n_total - n_unicos} ocorrências.")

    print("\n3. ANOMALIA DE 'OPERAÇÃO 0' (RADAR SIT)")
    if 'Operação' in df.columns:
        op_zero = df[df['Operação'] == '0']
        if not op_zero.empty:
            print(f"[ALERTA] {len(op_zero)} trabalhadores vinculados à 'Operação 0'.")
        else:
            print("[OK] Nenhum falso positivo gerado por 'Operação 0' do Radar SIT.")

    print("\n4. VALIDAÇÃO DO FILTRO TEMPORAL DE RESGATE")
    if 'flag_data_divergente' in df.columns:
        df['flag_data_divergente'] = df['flag_data_divergente'].astype(str).str.upper().str.strip()
        vazamentos = df[df['flag_data_divergente'] == 'TRUE']
        if not vazamentos.empty:
            print(f"[FALHA] {len(vazamentos)} registros romperam a barreira de 365 dias.")
        else:
            print("[OK] Filtro de 365 dias preservado.")

    print("\n5. AUDITORIA DE INTEGRIDADE TEMPORAL (Base Manual vs Radar SIT)")
    # Verifica se a trava de junção permitiu anos diferentes entre as bases
    if 'ano relatorio' in df.columns and 'Ano' in df.columns:
        # Apenas audita as linhas que de fato cruzaram com o SIT (onde 'Ano' não é nulo)
        cruzados = df[df['Ano'].notna()]
        inconsistentes = cruzados[cruzados['ano relatorio'] != cruzados['Ano']]
        if not inconsistentes.empty:
            print(f"[FALHA ESTRUTURAL] {len(inconsistentes)} linhas violaram o bloqueio de ano entre as bases.")
        else:
            print("[OK] 100% dos cruzamentos com o Radar SIT ocorreram no mesmo ano fiscal.")

    print("\n6. STATUS DE CONFIABILIDADE DOS ESTABELECIMENTOS")
    if 'flag_estabelecimento' in df.columns:
        contagem = df['flag_estabelecimento'].value_counts()
        for status, qtd in contagem.items():
            print(f"- {status}: {qtd}")
    
    print("\n--- AUDITORIA CONCLUÍDA ---")

if __name__ == '__main__':
    arquivo_alvo = r'E:\Code\enp\scripts\resultados_scripts\cruzamento_final_todos_anos_maio_2026_v11.xlsx'
    
    if os.path.exists(arquivo_alvo):
        auditar_base(arquivo_alvo)
    else:
        print(f"[ERRO] Arquivo não encontrado no caminho: {arquivo_alvo}")
