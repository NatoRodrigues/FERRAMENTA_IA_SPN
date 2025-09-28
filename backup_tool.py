# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox, ttk, font, filedialog
import requests 
import json
import threading

# --- CONFIGURAÇÃO DA API OPENROUTER ---
try:
    # !!! IMPORTANTE: COLOQUE SUA CHAVE DE API DO OPENROUTER AQUI !!!
    OPENROUTER_API_KEY = ""
    
    if not OPENROUTER_API_KEY or "SUA_CHAVE" in OPENROUTER_API_KEY:
        raise ValueError("Chave de API do OpenRouter não foi inserida. Por favor, edite o script.")

    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    HEADERS = {
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'http://localhost', 
        'X-Title': 'SPN Expert Agent'
    }
    
    MODELO_IA = "deepseek/deepseek-chat"
    print(f"[DEBUG] Configuração para API OpenRouter ({MODELO_IA}) realizada com sucesso.")
    
except Exception as e:
    print(f"[ERRO] Erro na configuração: {e}")
    HEADERS = None

# --- FUNÇÃO PRINCIPAL DE GERAÇÃO DE SCRIPT (CÉREBRO DA IA) ---
def gerar_script_com_ia(descricao_usuario):
    if not HEADERS:
        raise ConnectionError("API OpenRouter não inicializada.")

    # --- O "CÉREBRO" DEFINITIVO DO AGENTE ---
    prompt = f"""
    Você é um Agente de IA especialista em engenharia de desempenho e confiabilidade, programador sênior na linguagem de script da ferramenta Mercury. Sua tarefa é gerar scripts Mercury completos e sintaticamente corretos (SPN, RBD, CTMC) a partir de descrições em linguagem natural. A partir dos modelos da biblioteca, você deve criar novos modelos com base nas palavras-chaves detectadas, contanto que os novos códigos respeitem estritamente a sintaxe do Mercury Tool.

    a formula de TP é: TP = #E * 1/DELAY DA ULTIMA TRANSIÇAO NO CASO DE UM SISTEMA EM SERIE DE UMA UNICA ROTA.. caso tenha mais de uma rota, a regra da formula é a seguinte:


  ### REGRAS ESTRITAS DE SINTAXE OBRIGATÓRIAS
1.  **Transições**: Uma transição com qualquer valor no campo `delay` DEVE ser uma `timedTransition`. Use `immediateTransition` SOMENTE se não houver o campo `delay`.
2.  **Taxa de Serviço (µ)**: Ao construir uma expressão de `Throughput` (TP), a taxa de serviço (µ) é o inverso do delay (`µ = 1/delay`). Por exemplo, para `timedTransition T1(delay=25.0)`, a taxa na fórmula do TP seria `(1/25.0)`.
3.  **Métricas de Throughput (TP)**: A fórmula para TP DEVE seguir uma das duas regras abaixo, com base na arquitetura:
    * Para um **sistema em SÉRIE de ROTA ÚNICA**, a fórmula DEVE ser ((E{{#lugar_ultima_transicao}})*(1/delay1))
    * Para um **sistema com MÚLTIPLAS ROTAS PARALELAS**, a fórmula DEVE ser a soma das taxas de cada rota: `metric TP = stationaryAnalysis(method="direct", expression="((E{{#lugar_ultima_transicao}})*(1/delay1)) + ((E{{#LugarProc2}})*(1/delay2))");`
4.  **Cenários de Otimização**: Se o usuário pedir para "zerar o delay" de um componente, encontre a `timedTransition` correspondente no modelo e altere seu valor de `delay` para `0.0`. Recalcule a fórmula do TP de acordo com a nova taxa de serviço (que agora é infinita ou não contribui para a fórmula original).
5.  **Métricas de Desempenho (RT)**: A métrica de Tempo de Resposta (RT) depende do valor numérico do Throughput (TP). Se o usuário pedir o RT mas NÃO fornecer um valor numérico para o TP, gere o script com um placeholder, da seguinte forma: `metric RT_SYS = stationaryAnalysis(method="direct", expression="((...))/(VALOR_NUMERICO_DO_TP)");`
6.  **Saída Limpa**: O script final deve conter APENAS o código, sem explicações ou qualquer texto fora da estrutura do script.

### BIBLIOTECA DE MODELOS PADRÃO

#### Exemplo 1: SPN para Análise de Desempenho IoMT (Modelo de Pesquisa Principal)
- Descrição: Um modelo SPN de sistema fechado para calcular Throughput (TP) e Tempo de Resposta (RT_SYS). A fórmula do TP é a soma das taxas de serviço (inverso dos delays) das transições de processamento (TE2 e TE3), ponderada pelo número médio de trabalhos em cada estágio (P1 e P2).
- Script Mercury:
SPN Model{{
    place P1; place P2; place P3; place P4(tokens=1); place P5(tokens=1); place Wqueue(tokens=1);
    timedTransition TE0(inputs=[P3], outputs=[Wqueue], delay=3.0);
    timedTransition TE2(inputs=[P1], outputs=[P4, P3], delay=4.0);
    timedTransition TE3(inputs=[P2], outputs=[P5, P3], delay=5.0);
    timedTransition T_Imediata(inputs=[Wqueue, P4], outputs=[P1], delay=0.001);
    timedTransition T_imediata2(inputs=[Wqueue, P5], outputs=[P2], delay=0.001);
    metric TP = stationaryAnalysis(method="direct", expression="((E{{#P1}})*(1/4.0))+((E{{#P2}})*(1/5.0))");
    metric RT_SYS = stationaryAnalysis(method="direct", expression="((E{{#Wqueue}})+(E{{#P1}})+(E{{#P2}}))/(VALOR_NUMERICO_DO_TP)");
}}
main {{
    TP = solve(Model, TP);
    println(TP);
}}

#### Exemplo 2: Cenário de Otimização ("Zerar Delay")
- Descrição: Baseado no Exemplo 1, mas com o delay da transição 'TE2' zerado para uma análise de sensibilidade. A fórmula do TP é ajustada para refletir que a contribuição de TE2 não existe mais da mesma forma.
- Script Mercury:
SPN Model{{
    place P1; place P2; place P3; place P4(tokens=1); place P5(tokens=1); place Wqueue(tokens=1);
    timedTransition TE0(inputs=[P3], outputs=[Wqueue], delay=3.0);
    timedTransition TE2(inputs=[P1], outputs=[P4, P3], delay=0.0); // Delay zerado
    timedTransition TE3(inputs=[P2], outputs=[P5, P3], delay=5.0);
    timedTransition T_Imediata(inputs=[Wqueue, P4], outputs=[P1], delay=0.001);
    timedTransition T_imediata2(inputs=[Wqueue, P5], outputs=[P2], delay=0.001);
    metric TP = stationaryAnalysis(method="direct", expression="((E{{#P2}})*(1/5.0))"); // Fórmula de TP ajustada
    metric RT_SYS = stationaryAnalysis(method="direct", expression="((E{{#Wqueue}})+(E{{#P1}})+(E{{#P2}}))/(VALOR_NUMERICO_DO_TP)");
}}
main {{
    TP = solve(Model, TP);
    println(TP);
}}

#### Exemplo 2: Modelo de Falha e Reparo (Disponibilidade)
- Descrição: Modelo SPN simples para disponibilidade com estados Up e Down, usando MTTF e MTTR.
- Script Mercury:
SPN Model{{
        place Up(tokens=1); place Down;
        timedTransition Falha(inputs=[Up], outputs=[Down], delay=8760.0);
        timedTransition Reparo(inputs=[Down], outputs=[Up], delay=24.0);
        metric Disponibilidade = stationaryAnalysis(method="direct", expression="E{{#Up}}");
}}
main {{
    Disponibilidade = solve(Model, Disponibilidade);
    println(Disponibilidade);
}}

    ### SUA TAREFA
    Com base na extensa biblioteca e nas REGRAS ESTRITAS acima, analise a requisição do usuário a seguir e gere um script Mercury completo e funcional.

    #### REQUISIÇÃO DO USUÁRIO:
    "{descricao_usuario}"

    #### SCRIPT MERCURY GERADO:
    """
    
    print(f"Gerando script para: '{descricao_usuario[:60]}...'")
    
    data = {"model": MODELO_IA, "messages": [{"role": "user", "content": prompt}], "max_tokens": 4096}
    
    try:
        response = requests.post(API_URL, json=data, headers=HEADERS, timeout=120)
        if response.status_code == 200:
            response_json = response.json()
            script_gerado = response_json['choices'][0]['message']['content'].replace("```", "").strip()
            for keyword in ["SPN", "RBD", "CTMC", "k =", "lambda_ap", "mttf_hw"]:
                if keyword in script_gerado:
                    start_index = script_gerado.find(keyword)
                    script_gerado = script_gerado[start_index:]
                    break
            return script_gerado
        else:
            print(f"Falha ao gerar script. Código: {response.status_code}\nResposta: {response.text}")
            return f"ERRO: {response.text}"
    except requests.exceptions.Timeout:
        print("Erro: Timeout na requisição.")
        return "ERRO: A API demorou mais de 120 segundos para responder."
    except Exception as e:
        print(f"Erro na requisição: {e}")
        return f"ERRO NA REQUISIÇÃO: {e}"

# --- CLASSE DA APLICAÇÃO GUI (VERSÃO "VANILLA") ---
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Agente de IA para Geração de Modelos Mercury")
        self.root.geometry("800x600")

        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill='both', expand=True)

        label_input = tk.Label(main_frame, text="Descreva o Modelo (Ex: 'Gere um modelo IoMT com 4 componentes em série')")
        label_input.pack(pady=(0, 5), anchor='w')

        self.input_texto = tk.Text(main_frame, height=10, width=100, wrap=tk.WORD)
        self.input_texto.pack(fill='both', expand=True)

        self.btn_gerar = tk.Button(main_frame, text="Gerar Script Mercury", command=self.executar_geracao_em_thread, font=('Segoe UI', 10, 'bold'), pady=5)
        self.btn_gerar.pack(pady=10)

        label_output = tk.Label(main_frame, text="Script Mercury Gerado:")
        label_output.pack(pady=(10, 5), anchor='w')
        
        self.output_texto = tk.Text(main_frame, height=15, width=100, wrap=tk.WORD, font=("Courier New", 9))
        self.output_texto.pack(fill='both', expand=True)

    def executar_geracao_em_thread(self):
        descricao = self.input_texto.get("1.0", tk.END).strip()
        if not descricao:
            messagebox.showwarning("Aviso", "Por favor, descreva o modelo que você deseja gerar.")
            return
        
        self.btn_gerar.config(state='disabled', text="Gerando...")
        self.output_texto.delete('1.0', tk.END)
        self.output_texto.insert(tk.END, "Consultando o Agente de IA... Por favor, aguarde.")
        self.root.update()

        thread = threading.Thread(target=self.chamar_api_e_atualizar_ui, args=(descricao,))
        thread.start()

    def chamar_api_e_atualizar_ui(self, descricao):
        script_gerado = gerar_script_com_ia(descricao)
        self.root.after(0, self.atualizar_interface_com_resultado, script_gerado)

    def atualizar_interface_com_resultado(self, script_gerado):
        self.output_texto.delete('1.0', tk.END)
        self.output_texto.insert(tk.END, script_gerado)
        self.btn_gerar.config(state='normal', text="Gerar Script Mercury")

# --- PONTO DE ENTRADA DA APLICAÇÃO ---
if __name__ == "__main__":
    if HEADERS is None:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Erro Crítico", "A API não foi configurada corretamente. Verifique o console.")
    else:
        root = tk.Tk()
        app = App(root)
        root.mainloop()