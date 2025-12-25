import zmq
import json
import os
from datetime import datetime

class AndroidServer:
    def __init__(self, host="*", port=5555):
        self.host = host
        self.port = port
        self.message_count = 0
        self.data_file = "android_messages.json"
        self.load_existing_data()
    
    def load_existing_data(self):
        """Загружает существующие данные из файла"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data:
                        self.message_count = data[-1].get('packet_number', 0)
                        print(f"Loaded {len(data)} existing messages")
                        print(f"Last packet number: {self.message_count}")
            else:
                print(f"Data file '{self.data_file}' not found, creating new")
        except Exception as e:
            print(f"Error loading data: {e}")
            self.message_count = 0
    
    def save_message(self, message):
        """Сохраняет сообщение в файл"""
        self.message_count += 1
        timestamp = datetime.now()
        
        message_data = {
            "packet_number": self.message_count,
            "timestamp": timestamp.isoformat(),
            "time_human": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "message": message,
            "source": "Android",
            "server_received_at": datetime.now().strftime("%H:%M:%S")
        }
        
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            else:
                existing_data = []
            
            existing_data.append(message_data)
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
            print(f" Message saved to '{self.data_file}' (Packet #{self.message_count})")
            return True
            
        except Exception as e:
            print(f" Error saving message: {e}")
            return False
    
    def print_all_messages(self):
        """Выводит все сохраненные сообщения на экран"""
        print("\n" + "="*70)
        print("СОХРАНЕННЫЕ ДАННЫЕ ИЗ ANDROID:")
        print("="*70)
        
        try:
            if not os.path.exists(self.data_file):
                print("Файл данных не найден")
                return
            
            with open(self.data_file, 'r', encoding='utf-8') as f:
                messages = json.load(f)
            
            if not messages:
                print("Нет сохраненных сообщений")
                return
            
            print(f"Всего сообщений: {len(messages)}")
            print(f"Последний пакет: #{self.message_count}")
            print("-"*70)
            
            for msg in messages:
                print(f"Пакет #{msg.get('packet_number', 'N/A')}")
                print(f"Время: {msg.get('time_human', 'N/A')}")
                print(f"Сообщение: {msg.get('message', 'N/A')}")
                print(f"Источник: {msg.get('source', 'N/A')}")
                print("-"*70)
            
            print("\n СТАТИСТИКА:")
            print(f"• Всего пакетов: {len(messages)}")
            print(f"• Первое сообщение: {messages[0].get('time_human', 'N/A')}")
            print(f"• Последнее сообщение: {messages[-1].get('time_human', 'N/A')}")
            
        except Exception as e:
            print(f"Ошибка при чтении данных: {e}")
        
        print("="*70 + "\n")
    
    def print_statistics(self):
        """Выводит статистику"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
                
                print("\n СТАТИСТИКА СЕРВЕРА:")
                print(f"• Всего получено пакетов: {self.message_count}")
                print(f"• Сохранено в файле: {len(messages)} сообщений")
                print(f"• Файл данных: {self.data_file}")
                
                if messages:
                    print(f"• Диапазон времени: {messages[0].get('time_human')} - {messages[-1].get('time_human')}")
            else:
                print("Файл данных еще не создан")
                
        except Exception as e:
            print(f"Ошибка статистики: {e}")
    
    def clear_data(self):
        """Очищает все сохраненные данные"""
        try:
            if os.path.exists(self.data_file):
                os.remove(self.data_file)
                self.message_count = 0
                print(f" Данные очищены. Файл '{self.data_file}' удален")
            else:
                print("Файл данных не найден")
        except Exception as e:
            print(f"Ошибка при очистке: {e}")
    
    def start_server(self):
        """Запускает сервер"""
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        
        try:
            socket.bind(f"tcp://{self.host}:{self.port}")
            print("="*60)
            print(" ANDROID ZMQ СЕРВЕР ЗАПУЩЕН")
            print("="*60)
            print(f"Порт: {self.port}")
            print(f"Файл данных: {self.data_file}")
            print(f"Текущий счетчик пакетов: {self.message_count}")
            print("\n ДОСТУПНЫЕ КОМАНДЫ:")
            print("  'status'  - Показать статистику")
            print("  'show'    - Показать все сообщения")
            print("  'clear'   - Очистить все данные")
            print("  'exit'    - Остановить сервер")
            print("  'help'    - Показать это меню")
            print("="*60)
            print("Ожидание подключений Android...\n")
            
            while True:
                try:
                    import sys
                    import select
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        command = sys.stdin.readline().strip().lower()
                        self.handle_command(command)
                except:
                    pass
                
                try:
                    message_bytes = socket.recv(zmq.NOBLOCK)
                    message = message_bytes.decode('utf-8')
                    
                    print(f"\n📱 ПОЛУЧЕНО ОТ ANDROID: {message}")
                    
                    if self.save_message(message):
                        print(f"💾 Сохранено как пакет #{self.message_count}")
                    
                    response = f"Hello from Server! Received packet #{self.message_count}"
                    socket.send(response.encode('utf-8'))
                    print(f"📤 Ответ отправлен: {response}")
                    
                except zmq.Again:
                    continue
                    
        except KeyboardInterrupt:
            print("\n\n Сервер остановлен пользователем")
        except Exception as e:
            print(f"\n Ошибка сервера: {e}")
        finally:
            print("\n ФИНАЛЬНАЯ СТАТИСТИКА:")
            print(f"• Всего обработано пакетов: {self.message_count}")
            print(f"• Данные сохранены в: {self.data_file}")
            print("="*60)
            socket.close()
            context.term()
    
    def handle_command(self, command):
        """Обрабатывает команды с консоли"""
        if command == "status" or command == "stat":
            self.print_statistics()
        elif command == "show" or command == "print":
            self.print_all_messages()
        elif command == "clear":
            print("Вы уверены? Все данные будут удалены. Введите 'yes' для подтверждения:")
            confirm = input().strip().lower()
            if confirm == "yes":
                self.clear_data()
            else:
                print("Очистка отменена")
        elif command == "help" or command == "?":
            print("\n СПРАВКА ПО КОМАНДАМ:")
            print("  status  - Показать статистику сервера")
            print("  show    - Показать все сохраненные сообщения")
            print("  clear   - Очистить все данные (требует подтверждения)")
            print("  exit    - Остановить сервер")
            print("  help    - Показать эту справку\n")
        elif command == "exit" or command == "quit":
            print("\nЗавершение работы сервера...")
            raise KeyboardInterrupt
        elif command:
            print(f"Неизвестная команда: '{command}'. Введите 'help' для списка команд")

def main():
    print("Настройка Android ZMQ сервера...")
    
    HOST = "*"    # Принимать со всех интерфейсов
    PORT = 5555
    
    server = AndroidServer(HOST, PORT)
    server.start_server()

if __name__ == "__main__":
    main()