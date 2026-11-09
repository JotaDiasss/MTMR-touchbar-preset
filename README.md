# Meu preset e minha versão personalizada do MTMR

Este repositório guarda o layout da Touch Bar **e as alterações no aplicativo necessárias para reproduzir o resultado**. Apenas copiar `items.json` para o MTMR oficial não recupera todas as funções.

## O que está em cada lugar

| Arquivo | Conteúdo |
| --- | --- |
| `items.json` | Botões, tamanhos, alinhamentos, Spotify e animação habilitada |
| `patches/mtmr-personalizado.patch` | Alterações no código do MTMR |
| `UPSTREAM.json` | Revisão exata do projeto original e verificações dos downloads |
| `scripts/build.py` | Reconstrói o aplicativo personalizado |
| `scripts/install_preset.py` | Instala o preset e guarda uma cópia do anterior |
| `tests/main.swift` | Verifica o movimento do título e as pausas de 2 segundos |
| `LICENSE` | Licença MIT do MTMR original |

## Funções que dependem do aplicativo personalizado

- Dock que traz o aplicativo tocado para frente e pede a reabertura da janela quando o app continua rodando sem janelas, usando a mesma instância. Sem pontos de apps abertos, com indicador de foco separado, mais espaço entre ícones e imagens de alta resolução.
- Spotify em um bloco de largura fixa, centralizado na Touch Bar inteira.
- Tamanhos de fonte e imagens ajustáveis por `fontSize` e `image.pointSize`.
- Título longo que espera 2 segundos, desliza até o final, espera 2 segundos e volta ao início; o ciclo se repete. Títulos curtos ficam parados. A troca do título reinicia a animação; a consulta periódica da mesma música não a reinicia.
- Brilho compatível com o painel do Mac Apple Silicon usado nesta configuração.
- Brilho e volume com desenho personalizado dos controles deslizantes.

No `items.json`, `"marquee": true` habilita a animação do botão do título. Esses campos adicionais são implementados pelo patch deste repositório.

## Restaurar em outro Mac

O aplicativo desta configuração foi testado em um Mac **Apple Silicon, com macOS 27.2**. A compatibilidade com outros modelos e versões do macOS ainda não foi verificada. Uma nova compilação usa as ferramentas e a arquitetura do Mac em que for executada.

1. Instale o Spotify na pasta `/Applications`. O preset usa o ícone original do aplicativo, sem depender de uma pasta pessoal deste Mac.
2. Instale Python 3 e as ferramentas de linha de comando do Xcode, se necessário (`xcode-select --install`).
3. Na pasta deste repositório, execute:

   ```sh
   python3 scripts/build.py
   ```

   O processo baixa duas dependências oficiais fixadas por revisão e verifica a integridade por SHA-256, aplica o patch, compila, executa os testes da animação e gera `dist/MTMR.app`. A assinatura do aplicativo é local; não é uma distribuição assinada pelo desenvolvedor original.

4. Encerre o MTMR. Guarde uma cópia do aplicativo anterior e copie `dist/MTMR.app` para Aplicativos.
5. Instale o preset:

   ```sh
   python3 scripts/install_preset.py
   ```

6. Abra o MTMR e conceda Acessibilidade e a permissão para controlar o Spotify quando solicitadas.

O aplicativo instalado atualmente corresponde à versão `0.27-local.7`. O processo de compilação não instala nem abre o aplicativo automaticamente. O editor visual do projeto original não faz parte desta compilação; a configuração é editada no JSON.

## Manter o preset atualizado

Se o repositório estiver em `~/Library/Application Support/MTMR`, o `items.json` já é o arquivo ativo da Touch Bar. Depois de ajustar a configuração, versione as mudanças normalmente. Ao modificar o código do aplicativo, atualize também o patch e os testes; não basta salvar o JSON. Atualizações futuras do MTMR precisam preservar ou reaplicar esse patch.

Os diretórios `.build/` e `dist/` são gerados e ficam fora do Git. Para manter uma cópia do aplicativo pronto para uso, guarde o ZIP do aplicativo nos arquivos de uma Release ou em seu backup pessoal.

## Origem

Base: [Toxblh/MTMR](https://github.com/Toxblh/MTMR), revisão `fd958e420074330be900f3c19a8a09ead93d998b`. As alterações locais são preservadas como patch sobre essa revisão. Os recursos do aplicativo são recuperados do DMG oficial 0.27; o código e o framework usados para compilar vêm da revisão fixada. Os valores completos de verificação estão em `UPSTREAM.json`.

MTMR é distribuído sob a licença MIT; os créditos e a licença original foram preservados. O nome e o ícone do Spotify pertencem aos seus titulares e são carregados da instalação local do aplicativo.
