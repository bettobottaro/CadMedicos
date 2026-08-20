"""Utilitários para interface gráfica."""

def center_window(window):
    """Centraliza uma janela na tela."""
    window.update_idletasks()
    
    # Obter dimensões da janela
    width = window.winfo_width()
    height = window.winfo_height()
    
    # Obter dimensões da tela
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Calcular posição centralizada
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    # Garantir que não fica fora da tela
    x = max(0, x)
    y = max(0, y)
    
    # Posicionar a janela
    window.geometry(f"+{x}+{y}")
