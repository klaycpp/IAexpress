import mysql.connector
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.uix.camera import Camera
from kivy.uix.boxlayout import BoxLayout
from zxing import BarCodeReader

class IALogin(Screen):
    def login(self):
        app = MDApp.get_running_app()
        app.check_login()

class DashboardScreen(Screen):
    criar_pedido_screen = ObjectProperty()  # Adicione esta linha

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.criar_pedido_screen = CriarPedidoScreen()  # Adicione esta linha

    def adicionar_pedido(self):
        # Acessando a instância do aplicativo
        app = MDApp.get_running_app()
        
        # Navegando para a tela CriarPedidoScreen
        app.root.current = 'criar_pedido_screen'

    def analisar_pedidos(self):
        print("Analisar Pedidos")

    def pedidos_em_rota(self):
        print("Pedidos em Rota")

    def pedidos_concluidos(self):
        print("Pedidos Concluídos")

class CriarPedidoScreen(Screen):   
    def adicionar_pedido(self, codigo_pedido, nome_cliente):
        try:
            # Conectar ao banco de dados
            db_connection = mysql.connector.connect(
                host="aws.connect.psdb.cloud",
                user="h69345ofhghl0c0fhrux",
                password="pscale_pw_p1SFITsCwIi48iIcYyTlmbZ4ZukbfZMMBo58ocNAfXx",
                database="banco"
            )
            cursor = db_connection.cursor()
            
            # Inserir o novo pedido na tabela de pedidos
            query = "INSERT INTO pedidos (codigo_pedido, nome_cliente) VALUES (%s, %s)"
            cursor.execute(query, (codigo_pedido, nome_cliente))
            
            # Confirmar a transação
            db_connection.commit()
            
            print("Pedido adicionado com sucesso!")
            
        except mysql.connector.Error as err:
            print(f"Erro ao inserir o pedido no banco de dados: {err}")
            
        finally:
            # Fechar conexão com o banco de dados
            if 'db_connection' in locals() and db_connection.is_connected():
                cursor.close()
                db_connection.close()

    def escanear_qr_code(self):
        # Criar uma instância do leitor de código de barras
        barcode_reader = BarCodeReader()
        
        # Tentar escanear o código QR
        try:
            # Obter o resultado do escaneamento
            result = barcode_reader.decode(self.ids.usuario_field.text)
            
            # Verificar se o resultado foi encontrado
            if result:
                # Exibir o resultado em um Popup
                popup = Popup(title='Resultado do Escaneamento', content=Label(text=result), size_hint=(None, None), size=(400, 400))
                popup.open()
            else:
                # Exibir mensagem de erro se o código QR não foi encontrado
                popup = Popup(title='Erro', content=Label(text='Código QR não encontrado'), size_hint=(None, None), size=(400, 400))
                popup.open()
        except Exception as e:
            # Exibir mensagem de erro se houver algum problema no escaneamento
            popup = Popup(title='Erro', content=Label(text=f'Erro ao escanear código QR: {e}'), size_hint=(None, None), size=(400, 400))
            popup.open()    
    def abrir_camera(self):
        # Criar uma instância da câmera
        self.camera = Camera(resolution=(640, 480), play=True)

        # Criar um layout para a câmera e botão de captura
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.camera)

        # Botão para capturar a imagem
        button_capture = Button(text="Capturar", size_hint=(1, 0.1))
        button_capture.bind(on_press=self.capture_image)
        layout.add_widget(button_capture)

        # Criar um popup para exibir a câmera
        self.popup = Popup(title="Câmera", content=layout, size_hint=(0.8, 0.8))
        self.popup.open()

    def capture_image(self, instance):
        # Tirar uma foto e salvar
        self.camera.export_to_png("captured_image.png")

        # Fechar o popup
        self.popup.dismiss()    

    def criar_pedido1(self, codigo_pedido, nome_cliente):
        # Chamar o método para adicionar o pedido ao banco de dados
        self.adicionar_pedido(codigo_pedido, nome_cliente)       

class IAScreenManager(ScreenManager):
    pass

class CardButton(Button):
    pass

class IA(MDApp):
    def build(self):
        if not hasattr(self, 'sm'):
            self.title='Iago Express'
            self.theme_cls.theme_style = "Dark"
            self.theme_cls.primary_palette = "DeepPurple"
            Builder.load_file("login.kv")  # Carregar o arquivo KV da tela de login
            Builder.load_file("dashboard.kv")  # Carregar o arquivo KV da tela do dashboard
            Builder.load_file("criarpedido.kv")  # Carregar o novo arquivo KV da tela de criação de pedidos
            self.sm = IAScreenManager()
            self.sm.add_widget(IALogin(name='login_screen'))
            self.sm.add_widget(DashboardScreen(name='dashboard_screen'))
            self.sm.add_widget(CriarPedidoScreen(name='criar_pedido_screen'))  # Adicionando a nova tela
        return self.sm

    def check_login(self):
        # Acessando os valores dos campos de texto
        username = self.root.get_screen('login_screen').ids.usuario_field.text
        password = self.root.get_screen('login_screen').ids.password_field.text
        login_status = self.root.get_screen('login_screen').ids.login_status
        
        # Conectar ao banco de dados
        try:
            db_connection = mysql.connector.connect(
                host="aws.connect.psdb.cloud",
                user="h69345ofhghl0c0fhrux",
                password="pscale_pw_p1SFITsCwIi48iIcYyTlmbZ4ZukbfZMMBo58ocNAfXx",
                database="banco"
            )
            cursor = db_connection.cursor()
            
            # Consulta SQL para verificar as credenciais
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            
            if user:
                login_status.text = "Login bem-sucedido"
                # Mudar para a tela do dashboard
                self.root.current = "dashboard_screen"
            else:
                login_status.text = "Nome de usuário ou senha incorretos"
                
        except mysql.connector.Error as err:
            login_status.text = f"Erro ao conectar ao banco de dados: {err}"
            
        finally:
            # Fechar conexão com o banco de dados
            if 'db_connection' in locals() and db_connection.is_connected():
                cursor.close()
                db_connection.close()

    def enviar_pedido_com_foto(self, foto, codigo_pedido, nome_cliente):
        try:
            # Conectar ao banco de dados
            db_connection = mysql.connector.connect(
                host="aws.connect.psdb.cloud",
                user="h69345ofhghl0c0fhrux",
                password="pscale_pw_p1SFITsCwIi48iIcYyTlmbZ4ZukbfZMMBo58ocNAfXx",
                database="banco"
            )
            cursor = db_connection.cursor()
            
            # Ler a imagem como binário
            with open(foto, 'rb') as f:
                foto_binario = f.read()
            
            # Inserir o novo pedido na tabela de pedidos
            query = "INSERT INTO pedidos (codigo_pedido, nome_cliente, foto) VALUES (%s, %s, %s)"
            cursor.execute(query, (codigo_pedido, nome_cliente, foto_binario))
            
            # Confirmar a transação
            db_connection.commit()
            
            print("Pedido adicionado com sucesso!")
            
        except mysql.connector.Error as err:
            print(f"Erro ao inserir o pedido no banco de dados: {err}")
            
        finally:
            # Fechar conexão com o banco de dados
            if 'db_connection' in locals() and db_connection.is_connected():
                cursor.close()
                db_connection.close()

if __name__ == "__main__":
    Window.size = (360, 640)
    IA().run()
