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
    Você é um Agente de IA especialista em engenharia de desempenho e confiabilidade, programador sênior na linguagem de script da ferramenta Mercury para Redes de Petri Estocásticas (SPN).
    Sua principal tarefa é gerar scripts Mercury completos e sintaticamente corretos (SPN, RBD, CTMC) a partir de descrições em linguagem natural. A partir dos modelos da biblioteca, você deve criar novos modelos com base nas palavras-chaves detectadas, contanto que os novos códigos respeitem estritamente a sintaxe do Mercury Tool.
    SÓ ADICIONE COMENTÁRIOS COM // OU COM FUNÇÃO PRINTIN()
    a formula de TP é: TP = #E * 1/DELAY DA ULTIMA TRANSIÇAO NO CASO DE UM SISTEMA EM SERIE DE UMA UNICA ROTA.. caso tenha mais de uma rota, a regra da formula é a seguinte:
    NÃO CONCATENE VARIAVEL COM STRING.
    SÓ ADICIONE COMENTÁRIOS COM // em cada linha OU COM FUNÇÃO PRINTIN()
    ### REGRAS ESTRITAS DE SINTAXE OBRIGATÓRIAS
    1. **Transições**: Uma transição com qualquer valor no campo `delay` DEVE ser uma `timedTransition`. Use `immediateTransition` SOMENTE se não houver o campo `delay`.
    2. **Taxa de Serviço (µ)**: Ao construir uma expressão de `Throughput` (TP), a taxa de serviço (µ) é o inverso do delay (`µ = 1/delay`). Por exemplo, para `timedTransition T1(delay=25.0)`, a taxa na fórmula do TP seria `(1/25.0)`.
    3. **Métricas de Throughput (TP)**: A fórmula para TP DEVE seguir uma das duas regras abaixo, com base na arquitetura:
       * Para um **sistema em SÉRIE de ROTA ÚNICA**, a fórmula DEVE ser ((E{{#lugar_ultima_transicao}})*(1/delay1))
       * Para um **sistema com MÚLTIPLAS ROTAS PARALELAS**, a fórmula DEVE ser a soma das taxas de cada rota: `metric TP = stationaryAnalysis(method="direct", expression="((E{{#lugar_ultima_transicao}})*(1/delay1)) + ((E{{#LugarProc2}})*(1/delay2))");`
    4. **Cenários de Otimização**: Se o usuário pedir para "zerar o delay" de um componente, encontre a `timedTransition` correspondente no modelo e altere seu valor de `delay` para `0.0`. Recalcule a fórmula do TP de acordo com a nova taxa de serviço (que agora é infinita ou não contribui para a fórmula original).
    5. **Métricas de Desempenho (RT)**: A métrica de Tempo de Resposta (RT) depende do valor numérico do Throughput (TP). Se o usuário pedir o RT mas NÃO fornecer um valor numérico para o TP, gere o script com um placeholder, da seguinte forma: `metric RT_SYS = stationaryAnalysis(method="direct", expression="((...))/(VALOR_NUMERICO_DO_TP)");`
    OBS:Mesmo com o delay zerado(delay nunca deve ser ZERADO de fato, apenas um valor aproximado de zero tipo 0.0001), a formula deve ser aplicada, pois será somado também a probabilidade de tokens em cada fila.
    6. **Texto**: O script final deve conter APENAS o código, mas também pode conter string de texto com a função println().     NÃO USE FUNÇÕES QUE NÃO EXISTEM NO MERCURY. SEJA EXTREMAMENTE ORTODOXO.
    NÃO CONCATENE VARIAVEL COM STRING.
    ### BIBLIOTECA DE MODELOS PADRÃO
    SÓ ADICIONE COMENTÁRIOS COM // em cada linha OU COM FUNÇÃO PRINTIN()

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
    - Descrição: Baseado no Exemplo 1, mas com o delay da transição 'TE2' delay nunca deve ser ZERADO de fato, apenas um valor aproximado de zero tipo 0.0001
    - Script Mercury:
    SPN Model{{
        place P1; place P2; place P3; place P4(tokens=1); place P5(tokens=1); place Wqueue(tokens=1);
        timedTransition TE0(inputs=[P3], outputs=[Wqueue], delay=3.0);
        timedTransition TE2(inputs=[P1], outputs=[P4, P3], delay=0.0001); // delay nunca deve ser ZERADO de fato, apenas um valor aproximado de zero tipo 0.0001
        timedTransition TE3(inputs=[P2], outputs=[P5, P3], delay=5.0);
        timedTransition T_Imediata(inputs=[Wqueue, P4], outputs=[P1], delay=0.001);
        timedTransition T_imediata2(inputs=[Wqueue, P5], outputs=[P2], delay=0.001);
        metric TP = stationaryAnalysis(method="direct", expression="((E{{#P1}})*(1/0.001))+((E{{#P2}})*(1/5.0))"); // Fórmula de TP ajustada
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
    NÃO CONCATENE VARIAVEL COM STRING.
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
# --- CLASSE DA APLICAÇÃO GUI ---
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Agente de IA para Geração de Modelos Mercury")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f4f7")

        # --- MENU ---
        menubar = tk.Menu(root)
        root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Salvar Script", command=self.salvar_script)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=root.quit)
        menubar.add_cascade(label="Arquivo", menu=file_menu)

        ajuda_menu = tk.Menu(menubar, tearoff=0)
        ajuda_menu.add_command(label="Sobre", command=self.mostrar_sobre)
        menubar.add_cascade(label="Ajuda", menu=ajuda_menu)

        # --- FRAME PRINCIPAL ---
        main_frame = tk.Frame(root, bg="#f0f4f7", padx=10, pady=10)
        main_frame.pack(fill='both', expand=True)

        label_input = tk.Label(main_frame, text="Descreva o Modelo:", font=("Segoe UI", 11, "bold"), bg="#f0f4f7")
        label_input.pack(pady=(0, 5), anchor='w')

        input_frame = tk.Frame(main_frame, bg="#f0f4f7")
        input_frame.pack(fill='both', expand=True)

        self.input_texto = tk.Text(input_frame, height=8, wrap=tk.WORD, font=("Segoe UI", 10))
        self.input_texto.pack(side="left", fill="both", expand=True)

        scrollbar_in = tk.Scrollbar(input_frame, command=self.input_texto.yview)
        scrollbar_in.pack(side="right", fill="y")
        self.input_texto.config(yscrollcommand=scrollbar_in.set)

        self.btn_gerar = tk.Button(main_frame, text="🚀 Gerar Script Mercury", command=self.executar_geracao_em_thread,
                                   font=('Segoe UI', 11, 'bold'), bg="#0078D7", fg="white", relief="flat", padx=10, pady=8)
        self.btn_gerar.pack(pady=12)

        label_output = tk.Label(main_frame, text="Script Mercury Gerado:", font=("Segoe UI", 11, "bold"), bg="#f0f4f7")
        label_output.pack(pady=(10, 5), anchor='w')
        
        output_frame = tk.Frame(main_frame, bg="#f0f4f7")
        output_frame.pack(fill='both', expand=True)

        self.output_texto = tk.Text(output_frame, height=18, wrap=tk.WORD, font=("Courier New", 10), bg="#1e1e1e", fg="#d4d4d4", insertbackground="white")
        self.output_texto.pack(side="left", fill="both", expand=True)

        scrollbar_out = tk.Scrollbar(output_frame, command=self.output_texto.yview)
        scrollbar_out.pack(side="right", fill="y")
        self.output_texto.config(yscrollcommand=scrollbar_out.set)

    def executar_geracao_em_thread(self):
        descricao = self.input_texto.get("1.0", tk.END).strip()
        if not descricao:
            messagebox.showwarning("Aviso", "Por favor, descreva o modelo que você deseja gerar.")
            return
        
        self.btn_gerar.config(state='disabled', text="⏳ Gerando...")
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
        self.btn_gerar.config(state='normal', text="🚀 Gerar Script Mercury")

    def salvar_script(self):
        conteudo = self.output_texto.get("1.0", tk.END).strip()
        if not conteudo:
            messagebox.showwarning("Aviso", "Não há script para salvar.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os arquivos", "*.*")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(conteudo)
            messagebox.showinfo("Sucesso", f"Script salvo em:\n{file_path}")

    def mostrar_sobre(self):
        messagebox.showinfo("Sobre", "Agente de IA para Geração de Modelos Mercury\n\nDesenvolvido com Python + Tkinter.")

# --- PONTO DE ENTRADA DA APLICAÇÃO ---
if __name__ == "__main__":
    if HEADERS is None:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Erro Crítico", "A API não foi configurada corretamente.")
    else:
        root = tk.Tk()
        app = App(root)
        root.mainloop()
