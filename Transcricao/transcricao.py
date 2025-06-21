import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import which
import threading
import os
import datetime
from pathlib import Path
import json


class SpeechToTextApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Transcrição - Áudio e Vídeo")
        self.root.geometry("800x700")
        self.root.configure(bg='#f0f0f0')

        # Configurações
        self.recognizer = sr.Recognizer()
        self.current_file = None
        self.transcription_history = []

        # Criar interface
        self.create_interface()

        # Carregar histórico
        self.load_history()

    def create_interface(self):
        # Título
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', padx=0, pady=0)
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text="🎤 Sistema de Transcrição - Áudio e Vídeo",
                               font=('Arial', 16, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)

        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)

        # Seção de seleção de arquivo
        file_frame = tk.LabelFrame(main_frame, text="Selecionar Arquivo de Áudio ou Vídeo",
                                   font=('Arial', 12, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        file_frame.pack(fill='x', pady=(0, 15))

        file_inner = tk.Frame(file_frame, bg='#f0f0f0', padx=10, pady=10)
        file_inner.pack(fill='x')

        self.file_label = tk.Label(file_inner, text="Nenhum arquivo selecionado",
                                   bg='#f0f0f0', fg='#7f8c8d', font=('Arial', 10))
        self.file_label.pack(side='left', fill='x', expand=True)

        tk.Button(file_inner, text="📁 Escolher Arquivo", command=self.select_file,
                  bg='#3498db', fg='white', font=('Arial', 10, 'bold'),
                  padx=20, pady=5, relief='flat').pack(side='right', padx=(10, 0))

        # Seção de configurações
        config_frame = tk.LabelFrame(main_frame, text="Configurações",
                                     font=('Arial', 12, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        config_frame.pack(fill='x', pady=(0, 15))

        config_inner = tk.Frame(config_frame, bg='#f0f0f0', padx=10, pady=10)
        config_inner.pack(fill='x')

        tk.Label(config_inner, text="Idioma:", bg='#f0f0f0', font=('Arial', 10)).pack(side='left')

        self.language_var = tk.StringVar(value='pt-BR')
        language_combo = ttk.Combobox(config_inner, textvariable=self.language_var,
                                      values=['pt-BR', 'en-US', 'es-ES', 'fr-FR'],
                                      state='readonly', width=15)
        language_combo.pack(side='left', padx=(5, 20))

        # Botão de transcrição
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(fill='x', pady=(0, 15))

        self.transcribe_btn = tk.Button(button_frame, text="🚀 Iniciar Transcrição",
                                        command=self.start_transcription,
                                        bg='#27ae60', fg='white', font=('Arial', 12, 'bold'),
                                        padx=30, pady=10, relief='flat')
        self.transcribe_btn.pack()

        # Barra de progresso
        self.progress_var = tk.StringVar(value="Pronto para transcrever")
        self.progress_label = tk.Label(main_frame, textvariable=self.progress_var,
                                       bg='#f0f0f0', fg='#7f8c8d', font=('Arial', 10))
        self.progress_label.pack(pady=(0, 10))

        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.pack(fill='x', pady=(0, 15))

        # Área de texto para resultado
        result_frame = tk.LabelFrame(main_frame, text="Transcrição",
                                     font=('Arial', 12, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        result_frame.pack(fill='both', expand=True, pady=(0, 15))

        self.result_text = scrolledtext.ScrolledText(result_frame, height=12,
                                                     font=('Arial', 11), wrap='word',
                                                     bg='white', fg='#2c3e50')
        self.result_text.pack(fill='both', expand=True, padx=10, pady=10)

        # Botões de ação
        action_frame = tk.Frame(main_frame, bg='#f0f0f0')
        action_frame.pack(fill='x')

        tk.Button(action_frame, text="💾 Salvar Transcrição", command=self.save_transcription,
                  bg='#f39c12', fg='white', font=('Arial', 10, 'bold'),
                  padx=15, pady=5, relief='flat').pack(side='left', padx=(0, 10))

        tk.Button(action_frame, text="📋 Copiar", command=self.copy_to_clipboard,
                  bg='#9b59b6', fg='white', font=('Arial', 10, 'bold'),
                  padx=15, pady=5, relief='flat').pack(side='left', padx=(0, 10))

        tk.Button(action_frame, text="🗑️ Limpar", command=self.clear_text,
                  bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'),
                  padx=15, pady=5, relief='flat').pack(side='left', padx=(0, 10))

        tk.Button(action_frame, text="📊 Histórico", command=self.show_history,
                  bg='#34495e', fg='white', font=('Arial', 10, 'bold'),
                  padx=15, pady=5, relief='flat').pack(side='right')

    def select_file(self):
        file_types = [
            ('Arquivos de Áudio Recomendados', '*.wav *.mp3 *.flac *.m4a *.aac *.ogg'),
            ('Arquivos de Vídeo (Requer FFmpeg)', '*.mp4 *.avi *.mov *.mkv *.wmv *.webm'),
            ('Todos os Arquivos de Mídia', '*.wav *.mp3 *.flac *.m4a *.aac *.ogg *.mp4 *.avi *.mov *.mkv *.wmv *.webm'),
            ('MP3 files (Recomendado)', '*.mp3'),
            ('WAV files (Melhor qualidade)', '*.wav'),
            ('MP4 files (Requer FFmpeg)', '*.mp4'),
            ('Todos os arquivos', '*.*')
        ]

        filename = filedialog.askopenfilename(
            title="Selecionar arquivo de áudio ou vídeo",
            filetypes=file_types
        )

        if filename:
            self.current_file = filename
            self.file_label.config(text=f"📎 {os.path.basename(filename)}", fg='#27ae60')

    def check_ffmpeg_availability(self):
        """Verifica se FFmpeg está disponível"""
        try:
            import subprocess
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except:
            return False

    def convert_to_wav(self, input_file):
        """Converte arquivo de áudio/vídeo para WAV se necessário"""
        if input_file.lower().endswith('.wav'):
            return input_file

        try:
            file_ext = os.path.splitext(input_file.lower())[1]

            # Verificar se é arquivo de vídeo
            video_formats = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.webm']
            is_video = file_ext in video_formats

            if is_video:
                self.progress_var.set("Extraindo áudio do vídeo...")
                # Verificar se FFmpeg está disponível para vídeos
                if not self.check_ffmpeg_availability():
                    raise Exception("FFmpeg não encontrado. Para processar vídeos MP4, instale o FFmpeg:\n\n" +
                                    "1. Baixe em: https://ffmpeg.org/download.html\n" +
                                    "2. Ou execute: winget install ffmpeg\n" +
                                    "3. Ou use: choco install ffmpeg\n\n" +
                                    "Alternativamente, converta o MP4 para MP3 primeiro.")
            else:
                self.progress_var.set("Convertendo arquivo de áudio...")

            self.root.update()

            # Tentar diferentes métodos de carregamento
            audio = None

            # Método 1: Tentar com pydub normal
            try:
                audio = AudioSegment.from_file(input_file)
            except Exception as e1:
                # Método 2: Especificar formato explicitamente
                try:
                    if file_ext == '.mp4':
                        audio = AudioSegment.from_file(input_file, format="mp4")
                    elif file_ext == '.mp3':
                        audio = AudioSegment.from_file(input_file, format="mp3")
                    elif file_ext == '.m4a':
                        audio = AudioSegment.from_file(input_file, format="m4a")
                    else:
                        audio = AudioSegment.from_file(input_file)
                except Exception as e2:
                    # Método 3: Usar ffmpeg diretamente se disponível
                    if self.check_ffmpeg_availability():
                        try:
                            audio = AudioSegment.from_file(input_file)
                        except Exception as e3:
                            error_msg = f"Não foi possível carregar o arquivo.\n\n"
                            if is_video:
                                error_msg += "Para vídeos MP4, certifique-se de que:\n"
                                error_msg += "1. O FFmpeg está instalado\n"
                                error_msg += "2. O arquivo não está corrompido\n"
                                error_msg += "3. O formato é suportado\n\n"
                                error_msg += "Tente converter para MP3 primeiro."
                            else:
                                error_msg += f"Erro específico: {str(e3)}"
                            raise Exception(error_msg)
                    else:
                        error_msg = "Erro ao carregar arquivo de áudio.\n\n"
                        if is_video:
                            error_msg += "Para vídeos MP4, instale o FFmpeg.\n"
                        error_msg += f"Erro: {str(e1)}"
                        raise Exception(error_msg)

            if audio is None:
                raise Exception("Não foi possível carregar o arquivo de áudio/vídeo.")

            # Converter para formato adequado para reconhecimento
            self.progress_var.set("Otimizando áudio para transcrição...")
            self.root.update()

            # Configurações otimizadas para speech recognition
            audio = audio.set_frame_rate(16000).set_channels(1)

            # Para arquivos muito longos, aplicar normalização
            if len(audio) > 300000:  # Mais de 5 minutos
                self.progress_var.set("Otimizando áudio longo...")
                self.root.update()
                audio = audio.normalize()

            # Salvar como WAV temporário
            temp_wav = "temp_audio_converted.wav"
            audio.export(temp_wav, format="wav")

            return temp_wav

        except Exception as e:
            raise Exception(f"Erro ao processar arquivo: {str(e)}")

    def transcribe_audio(self, audio_file, language):
        """Transcreve o arquivo de áudio"""
        try:
            with sr.AudioFile(audio_file) as source:
                self.progress_var.set("Analisando arquivo de áudio...")
                self.root.update()

                # Ajustar para ruído ambiente
                self.recognizer.adjust_for_ambient_noise(source, duration=1)

                # Para arquivos longos, processar em chunks
                audio_length = source.DURATION if hasattr(source, 'DURATION') else None

                if audio_length and audio_length > 60:  # Mais de 1 minuto
                    return self.transcribe_long_audio(source, language)
                else:
                    # Áudio curto - processar normalmente
                    self.progress_var.set("Transcrevendo áudio...")
                    self.root.update()

                    audio_data = self.recognizer.record(source)
                    text = self.recognizer.recognize_google(audio_data, language=language)
                    return text

        except sr.UnknownValueError:
            raise Exception("Não foi possível entender o áudio. Verifique a qualidade da gravação.")
        except sr.RequestError as e:
            raise Exception(f"Erro no serviço de reconhecimento: {str(e)}")
        except Exception as e:
            raise Exception(f"Erro na transcrição: {str(e)}")

    def transcribe_long_audio(self, source, language):
        """Transcreve arquivos de áudio longos em partes"""
        transcription_parts = []
        chunk_duration = 30  # 30 segundos por chunk

        try:
            # Calcular número de chunks
            total_duration = source.DURATION if hasattr(source, 'DURATION') else 60
            num_chunks = int(total_duration / chunk_duration) + 1

            for i in range(num_chunks):
                try:
                    self.progress_var.set(f"Transcrevendo parte {i + 1} de {num_chunks}...")
                    self.root.update()

                    # Ler chunk específico
                    offset = i * chunk_duration
                    audio_data = self.recognizer.record(source, duration=chunk_duration, offset=offset)

                    # Transcrever chunk
                    chunk_text = self.recognizer.recognize_google(audio_data, language=language)
                    if chunk_text.strip():
                        transcription_parts.append(chunk_text)

                except sr.UnknownValueError:
                    # Pular partes que não podem ser entendidas
                    continue
                except Exception as e:
                    print(f"Erro no chunk {i + 1}: {str(e)}")
                    continue

            if not transcription_parts:
                raise Exception("Não foi possível transcrever nenhuma parte do áudio.")

            return " ".join(transcription_parts)

        except Exception as e:
            raise Exception(f"Erro ao processar áudio longo: {str(e)}")

    def start_transcription(self):
        if not self.current_file:
            messagebox.showwarning("Aviso", "Por favor, selecione um arquivo de áudio primeiro.")
            return

        # Desabilitar botão durante o processo
        self.transcribe_btn.config(state='disabled')
        self.progress_bar.start()

        # Executar transcrição em thread separada
        thread = threading.Thread(target=self.transcription_worker)
        thread.daemon = True
        thread.start()

    def transcription_worker(self):
        temp_file = None
        try:
            # Converter arquivo se necessário
            temp_file = self.convert_to_wav(self.current_file)

            # Transcrever
            language = self.language_var.get()
            transcription = self.transcribe_audio(temp_file, language)

            # Atualizar interface na thread principal
            self.root.after(0, self.transcription_complete, transcription, None)

        except Exception as e:
            self.root.after(0, self.transcription_complete, None, str(e))

        finally:
            # Limpar arquivo temporário
            if temp_file and temp_file != self.current_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

    def transcription_complete(self, transcription, error):
        # Reabilitar botão e parar progresso
        self.transcribe_btn.config(state='normal')
        self.progress_bar.stop()

        if error:
            self.progress_var.set("Erro na transcrição")
            messagebox.showerror("Erro", error)
        else:
            self.progress_var.set("Transcrição concluída com sucesso!")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, transcription)

            # Salvar no histórico
            self.add_to_history(transcription)

    def add_to_history(self, transcription):
        entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'file': os.path.basename(self.current_file) if self.current_file else 'Unknown',
            'language': self.language_var.get(),
            'transcription': transcription[:100] + '...' if len(transcription) > 100 else transcription,
            'full_text': transcription
        }
        self.transcription_history.append(entry)
        self.save_history()

    def save_transcription(self):
        text = self.result_text.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Aviso", "Não há transcrição para salvar.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Salvar transcrição"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Transcrição realizada em: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                    f.write(
                        f"Arquivo original: {os.path.basename(self.current_file) if self.current_file else 'N/A'}\n")
                    f.write(f"Idioma: {self.language_var.get()}\n")
                    f.write("-" * 50 + "\n\n")
                    f.write(text)

                messagebox.showinfo("Sucesso", f"Transcrição salva em: {filename}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar arquivo: {str(e)}")

    def copy_to_clipboard(self):
        text = self.result_text.get(1.0, tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("Sucesso", "Transcrição copiada para a área de transferência!")
        else:
            messagebox.showwarning("Aviso", "Não há texto para copiar.")

    def clear_text(self):
        self.result_text.delete(1.0, tk.END)
        self.progress_var.set("Pronto para transcrever")

    def show_history(self):
        if not self.transcription_history:
            messagebox.showinfo("Histórico", "Nenhuma transcrição no histórico.")
            return

        # Criar janela de histórico
        history_window = tk.Toplevel(self.root)
        history_window.title("Histórico de Transcrições")
        history_window.geometry("700x500")
        history_window.configure(bg='#f0f0f0')

        # Lista de histórico
        frame = tk.Frame(history_window, bg='#f0f0f0', padx=20, pady=20)
        frame.pack(fill='both', expand=True)

        tk.Label(frame, text="Histórico de Transcrições", font=('Arial', 14, 'bold'),
                 bg='#f0f0f0', fg='#2c3e50').pack(pady=(0, 15))

        # Treeview para mostrar histórico
        columns = ('Data/Hora', 'Arquivo', 'Idioma', 'Prévia')
        tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Adicionar dados do histórico
        for i, entry in enumerate(reversed(self.transcription_history)):
            timestamp = datetime.datetime.fromisoformat(entry['timestamp']).strftime('%d/%m/%Y %H:%M')
            tree.insert('', 'end', values=(
                timestamp,
                entry['file'],
                entry['language'],
                entry['transcription']
            ))

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Botão para ver transcrição completa
        def view_full_transcription():
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                index = len(self.transcription_history) - 1 - tree.index(selection[0])
                full_text = self.transcription_history[index]['full_text']

                # Mostrar texto completo
                text_window = tk.Toplevel(history_window)
                text_window.title("Transcrição Completa")
                text_window.geometry("600x400")

                text_widget = scrolledtext.ScrolledText(text_window, wrap='word', font=('Arial', 11))
                text_widget.pack(fill='both', expand=True, padx=10, pady=10)
                text_widget.insert(1.0, full_text)
                text_widget.config(state='disabled')

        btn_frame = tk.Frame(frame, bg='#f0f0f0')
        btn_frame.pack(fill='x', pady=(10, 0))

        tk.Button(btn_frame, text="Ver Transcrição Completa", command=view_full_transcription,
                  bg='#3498db', fg='white', font=('Arial', 10, 'bold'),
                  padx=20, pady=5, relief='flat').pack()

    def save_history(self):
        try:
            with open('transcription_history.json', 'w', encoding='utf-8') as f:
                json.dump(self.transcription_history, f, ensure_ascii=False, indent=2)
        except:
            pass

    def load_history(self):
        try:
            if os.path.exists('transcription_history.json'):
                with open('transcription_history.json', 'r', encoding='utf-8') as f:
                    self.transcription_history = json.load(f)
        except:
            self.transcription_history = []


def main():
    # Verificar dependências
    try:
        import speech_recognition
        import pydub
    except ImportError as e:
        print("Erro: Dependências não encontradas.")
        print("Execute os seguintes comandos para instalar:")
        print("pip install SpeechRecognition")
        print("pip install pydub")
        print("pip install pyaudio")
        print("\nPara suporte completo a vídeos MP4, instale também:")
        print("pip install ffmpeg-python")
        print("Ou baixe o FFmpeg em: https://ffmpeg.org/download.html")
        return

    root = tk.Tk()
    app = SpeechToTextApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()