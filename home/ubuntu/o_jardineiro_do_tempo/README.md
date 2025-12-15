# O Jardineiro do Tempo (The Time Gardener)

Um jogo criativo e original de simulação/puzzle desenvolvido com Pygame, onde o jogador manipula o fluxo do tempo localmente em seu jardim para gerenciar o crescimento de plantas e combater pragas.

## Como Jogar

### Instalação
1.  Certifique-se de ter o Python 3 instalado.
2.  Instale a biblioteca Pygame:
    ```bash
    pip install pygame
    ```

### Execução
1.  Navegue até o diretório `src` do projeto:
    ```bash
    cd o_jardineiro_do_tempo/src
    ```
2.  Execute o arquivo principal:
    ```bash
    python3 main.py
    ```

## Controles

| Ação | Tecla | Efeito |
| :--- | :--- | :--- |
| Mover | **WASD** ou **Setas** | Move o Jardineiro. |
| Interagir | **E** | Planta sementes (em solo vazio), Colhe plantas maduras, ou Remove ervas daninhas. |
| Acelerar Tempo | **Z** | Acelera o tempo em uma área 3x3 ao redor do Jardineiro (Custa Energia Temporal). |
| Reverter Tempo | **X** | Reverte o tempo em uma área 3x3 ao redor do Jardineiro (Custa Energia Temporal). |
| Sair | **ESC** | Fecha o jogo. |

## Mecânicas Principais

*   **Manipulação Temporal Localizada:** Use **Z** e **X** para acelerar o crescimento das plantas ou reverter o murchamento.
*   **Gerenciamento de Energia:** O uso da manipulação temporal consome Energia Temporal, que se regenera quando o Jardineiro está parado.
*   **Desafios:** Ervas daninhas e pragas (pontos vermelhos) surgem e ameaçam o jardim, exigindo intervenção rápida.
*   **Medidor de Beleza:** Mantenha este medidor alto colhendo plantas maduras e eliminando ameaças.

---
Desenvolvido por **Manus AI** como um projeto criativo.
[GDD do Jogo](/home/ubuntu/GDD_O_Jardineiro_do_Tempo.md)
