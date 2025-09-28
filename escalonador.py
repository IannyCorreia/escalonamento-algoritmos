import collections
import random
import copy

class Processo:
    """
    Classe para representar um processo, seus atributos e métricas de desempenho.
    """
    def __init__(self, pid, chegada, execucao, prioridade):
        self.pid = pid
        self.chegada = chegada
        self.execucao_total = execucao 
        self.prioridade = prioridade

        # Atributos que mudam durante a simulação
        self.tempo_restante = self.execucao_total
        
        # Métricas de resultado
        self.tempo_conclusao = 0
        self.tempo_retorno = 0
        self.tempo_espera = 0

    def __repr__(self):
        # Representação do objeto para facilitar a depuração
        return f"Processo(pid={self.pid}, chegada={self.chegada}, execucao={self.execucao_total}, prioridade={self.prioridade})"

def calcular_e_imprimir_resultados(nome_algoritmo, processos_finalizados, ordem_execucao, arquivo_saida):
    """
    Calcula os tempos médios e formata a saída para o console e para o arquivo.
    """
    total_tempo_espera = 0
    total_tempo_retorno = 0

    # Ordena por PID para exibição consistente
    processos_finalizados.sort(key=lambda p: p.pid)

    for p in processos_finalizados:
        p.tempo_retorno = p.tempo_conclusao - p.chegada
        p.tempo_espera = p.tempo_retorno - p.execucao_total
        total_tempo_espera += p.tempo_espera
        total_tempo_retorno += p.tempo_retorno
    
    tempo_medio_espera = total_tempo_espera / len(processos_finalizados)
    tempo_medio_retorno = total_tempo_retorno / len(processos_finalizados)

    # --- Monta o bloco de texto para saída ---
    saida = []
    saida.append(f"Resultados para o Algoritmo: {nome_algoritmo}")
    saida.append("-" * 30)
    saida.append(f"Ordem de Execução: {' -> '.join(ordem_execucao)}")
    saida.append("\nMétricas Individuais:")
    saida.append(f"{'Processo':<10}{'Tempo de Espera':<20}{'Tempo de Retorno':<20}")
    for p in processos_finalizados:
        saida.append(f"{p.pid:<10}{p.tempo_espera:<20}{p.tempo_retorno:<20}")
    
    saida.append("\nMétricas Gerais:")
    saida.append(f"Tempo Médio de Espera: {tempo_medio_espera:.2f}")
    saida.append(f"Tempo Médio de Retorno: {tempo_medio_retorno:.2f}")
    
    # Imprime no console
    print("\n".join(saida))

    # Grava no arquivo de saída
    with open(arquivo_saida, 'a', encoding='utf-8') as f:
        f.write("\n".join(saida))
        f.write("\n" + "-------" + "\n\n")

# --- Implementação dos Algoritmos de Escalonamento ---

def fcfs(processos):
    tempo_atual = 0
    ordem_execucao = []
    processos_ordenados = sorted(processos, key=lambda p: p.chegada)
    
    for p in processos_ordenados:
        if tempo_atual < p.chegada:
            tempo_atual = p.chegada
        
        ordem_execucao.append(p.pid)
        tempo_atual += p.execucao_total
        p.tempo_conclusao = tempo_atual
        
    return processos_ordenados, ordem_execucao

def sjf(processos):
    tempo_atual = 0
    ordem_execucao = []
    processos_finalizados = []
    
    while len(processos_finalizados) < len(processos):
        # Filtra processos que já chegaram e ainda não foram finalizados
        prontos = [p for p in processos if p.chegada <= tempo_atual and p not in processos_finalizados]
        
        if not prontos:
            tempo_atual += 1
            continue
            
        # Seleciona o processo com menor tempo de execução
        processo_atual = min(prontos, key=lambda p: p.execucao_total)
        
        ordem_execucao.append(processo_atual.pid)
        tempo_atual += processo_atual.execucao_total
        processo_atual.tempo_conclusao = tempo_atual
        processos_finalizados.append(processo_atual)
        
    return processos_finalizados, ordem_execucao

def round_robin(processos, quantum=4):
    tempo_atual = 0
    ordem_execucao = []
    processos_finalizados = []
    
    fila_prontos = collections.deque()
    processos_a_chegar = sorted(processos, key=lambda p: p.chegada)

    while len(processos_finalizados) < len(processos):
        # Adiciona processos que chegaram na fila de prontos
        while processos_a_chegar and processos_a_chegar[0].chegada <= tempo_atual:
            fila_prontos.append(processos_a_chegar.pop(0))

        if not fila_prontos:
            tempo_atual += 1
            continue

        processo_atual = fila_prontos.popleft()
        
        # Adiciona na ordem de execução se for a primeira vez
        if processo_atual.pid not in ordem_execucao:
            ordem_execucao.append(processo_atual.pid)
        
        tempo_executado = min(quantum, processo_atual.tempo_restante)
        tempo_atual += tempo_executado
        processo_atual.tempo_restante -= tempo_executado

        # Verifica novamente por processos que chegaram enquanto este executava
        while processos_a_chegar and processos_a_chegar[0].chegada <= tempo_atual:
            fila_prontos.append(processos_a_chegar.pop(0))

        if processo_atual.tempo_restante > 0:
            fila_prontos.append(processo_atual)
        else:
            processo_atual.tempo_conclusao = tempo_atual
            processos_finalizados.append(processo_atual)
            
    return processos_finalizados, ordem_execucao

def priority_scheduling(processos):
    tempo_atual = 0
    ordem_execucao = []
    processos_finalizados = []
    
    while len(processos_finalizados) < len(processos):
        prontos = [p for p in processos if p.chegada <= tempo_atual and p not in processos_finalizados]
        
        if not prontos:
            tempo_atual += 1
            continue
        
        # Seleciona o processo com menor valor de prioridade (maior prioridade)
        processo_atual = min(prontos, key=lambda p: p.prioridade)
        
        ordem_execucao.append(processo_atual.pid)
        tempo_atual += processo_atual.execucao_total
        processo_atual.tempo_conclusao = tempo_atual
        processos_finalizados.append(processo_atual)
        
    return processos_finalizados, ordem_execucao

def priority_multiple_queues(processos):
    # Simulação com 3 filas de prioridade: 1 (alta), 2 (média), 3 (baixa)
    # Dentro de cada fila, o algoritmo é FCFS.
    filas = {1: collections.deque(), 2: collections.deque(), 3: collections.deque()}
    
    tempo_atual = 0
    ordem_execucao = []
    processos_finalizados = []
    processos_a_chegar = sorted(processos, key=lambda p: p.chegada)
    
    while len(processos_finalizados) < len(processos):
        # Adiciona processos que chegaram às suas respectivas filas
        while processos_a_chegar and processos_a_chegar[0].chegada <= tempo_atual:
            processo = processos_a_chegar.pop(0)
            filas[processo.prioridade].append(processo)

        processo_atual = None
        if filas[1]:
            processo_atual = filas[1].popleft()
        elif filas[2]:
            processo_atual = filas[2].popleft()
        elif filas[3]:
            processo_atual = filas[3].popleft()
        
        if not processo_atual:
            tempo_atual += 1
            continue

        ordem_execucao.append(processo_atual.pid)
        tempo_atual += processo_atual.execucao_total
        processo_atual.tempo_conclusao = tempo_atual
        processos_finalizados.append(processo_atual)
        
    return processos_finalizados, ordem_execucao

def lottery_scheduling(processos):
    # Mapeamento de prioridade para bilhetes (menor prioridade = mais bilhetes)
    mapa_bilhetes = {1: 20, 2: 10, 3: 5}
    
    tempo_atual = 0
    ordem_execucao_sequencial = []
    processos_finalizados = []
    processos_a_chegar = sorted(processos, key=lambda p: p.chegada)

    while len(processos_finalizados) < len(processos):
        prontos = [p for p in processos if p.chegada <= tempo_atual and p not in processos_finalizados]
        
        if not prontos:
            # Adiciona processos que chegaram durante o tempo ocioso
            while processos_a_chegar and processos_a_chegar[0].chegada <= tempo_atual:
                prontos.append(processos_a_chegar.pop(0))
            if not prontos:
                tempo_atual += 1
                continue

        # Cria a urna de bilhetes
        urna = []
        for p in prontos:
            num_bilhetes = mapa_bilhetes.get(p.prioridade, 1)
            urna.extend([p.pid] * num_bilhetes)
            
        if not urna:
            tempo_atual += 1
            continue
        
        # Sorteia o vencedor
        pid_vencedor = random.choice(urna)
        processo_atual = next(p for p in prontos if p.pid == pid_vencedor)

        # Adiciona na ordem de execução se for diferente do último
        if not ordem_execucao_sequencial or ordem_execucao_sequencial[-1] != processo_atual.pid:
            ordem_execucao_sequencial.append(processo_atual.pid)
            
        # Executa por 1 unidade de tempo
        tempo_atual += 1
        processo_atual.tempo_restante -= 1

        if processo_atual.tempo_restante == 0:
            processo_atual.tempo_conclusao = tempo_atual
            processos_finalizados.append(processo_atual)

    return processos_finalizados, ordem_execucao_sequencial

# --- Função Principal ---

def main():
    # Definição dos processos de entrada
    lista_processos = [
        Processo(pid='P1', chegada=0, execucao=5, prioridade=2),
        Processo(pid='P2', chegada=2, execucao=3, prioridade=1),
        Processo(pid='P3', chegada=4, execucao=8, prioridade=3),
        Processo(pid='P4', chegada=5, execucao=6, prioridade=2),
        Processo(pid='P5', chegada=11, execucao=8, prioridade=1),
    ]

    arquivo_saida = "resultados_escalonamento.txt"
    # Limpa o arquivo de saída antes de começar
    with open(arquivo_saida, 'w') as f:
        f.write("--- Simulação de Algoritmos de Escalonamento ---\n\n")

    # Dicionário de algoritmos para facilitar a chamada
    algoritmos = {
        "FCFS": fcfs,
        "SJF (Não-Preemptivo)": sjf,
        "Round Robin (Quantum=4)": lambda p: round_robin(p, quantum=4),
        "Priority Scheduling (Não-Preemptivo)": priority_scheduling,
        "Priority Scheduling - Multiple Queues": priority_multiple_queues,
        "Lottery Scheduling": lottery_scheduling
    }
    
    for nome, funcao_algoritmo in algoritmos.items():
        # Usa deepcopy para garantir que a lista original de processos não seja alterada
        processos_para_simular = copy.deepcopy(lista_processos)
        
        processos_finalizados, ordem_execucao = funcao_algoritmo(processos_para_simular)
        
        calcular_e_imprimir_resultados(nome, processos_finalizados, ordem_execucao, arquivo_saida)

if __name__ == "__main__":
    main()