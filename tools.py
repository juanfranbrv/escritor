def write_markdown_file(content, filename):
  """Writes the given content as a markdown file to the local directory.

  Args:
    content: The string content to write to the file.
    filename: The filename to save the file as.
  """
  with open(f"{filename}.md", "w") as f:
    f.write(content)


def contar_palabras(text):
    words=text.split()
    return len(words)

def human_in_the_loop():
    """
    Pausa la ejecución del script para intervención humana.
    - Si se pulsa ENTER, el script continúa.
    - Si se introduce cualquier otro carácter, el script se detiene.
    """
    from rich import print
    print("[bold blue]🛑 Pausa: Presiona ENTER para continuar o escribe cualquier cosa para detener el script:[/bold blue]",end="")
    respuesta = input()
    if respuesta.strip():
        print("[bold red]❌ Script detenido por el usuario.[/bold red]")
        exit()


