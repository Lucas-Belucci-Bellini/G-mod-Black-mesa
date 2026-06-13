Como especialista na Source Engine, posso te ajudar com isso. Montar assets de jogos externos no Garry's Mod é um processo direto, mas requer precisão nos caminhos dos arquivos. O Black Mesa é um caso peculiar devido às pesadas modificações que a Crowbar Collective fez na engine original, então precisamos ter cuidado extra.

Para facilitar o processo, fornecemos um script de automação para realizar toda a configuração. Escolha o método que preferir:

---

## ⚡ Método Automático (Recomendado)

O script automatiza a detecção de caminhos da Steam e altera as configurações de forma segura.

### Como Executar:
1. **Via Batch (Windows)**: Dê um duplo clique no arquivo [run.bat](file:///c:/G-mod-Black-mesa/run.bat).
2. **Via Terminal**: Rode o comando abaixo no terminal da pasta do projeto:
   ```bash
   python automate_mount.py
   ```
3. O script confirmará os caminhos detectados e criará um backup de segurança do seu `mount.cfg` antes de modificá-lo.

---

## 🛠️ Método Manual: Guia Passo a Passo

Se preferir fazer a montagem manualmente, siga os passos abaixo:


Passo 1: Preparando o Garry's Mod (Branch x86-64)
Antes de montar os arquivos, certifique-se de que o seu Garry's Mod está rodando na versão 64-bits, o que melhora significativamente o desempenho ao carregar muitos assets e mapas grandes.

Abra a sua biblioteca da Steam.

Clique com o botão direito no Garry's Mod e selecione Propriedades.

Vá até a aba Betas.

No menu suspenso de Participação Beta, selecione: x86-64 - Chromium + 64-bit binaries.

Aguarde o download da atualização e inicie o jogo pelo menos uma vez para garantir que as pastas de configuração sejam geradas corretamente.

Passo 2: Localizando os Diretórios Corretos
Você precisará saber o caminho exato de instalação do Black Mesa e onde encontrar o arquivo de montagem do Garry's Mod.

1. Caminho do Black Mesa:
O diretório que precisamos é a pasta bms, que contém o conteúdo principal do jogo. O caminho padrão geralmente é:
C:\Program Files (x86)\Steam\steamapps\common\Black Mesa\bms
(Nota: Se você instalou em outro HD, ajuste a letra da unidade e o caminho de acordo).

2. Caminho do mount.cfg do Garry's Mod:
Este é o arquivo de texto onde declaramos quais jogos o GMod deve carregar. O caminho padrão é:
C:\Program Files (x86)\Steam\steamapps\common\GarrysMod\garrysmod\cfg\mount.cfg

Passo 3: Editando o arquivo mount.cfg
Agora vamos vincular o diretório do Black Mesa ao Garry's Mod.

Navegue até a pasta cfg do Garry's Mod e abra o arquivo mount.cfg usando um editor de texto simples (como o Bloco de Notas ou o Notepad++).

Você verá um código parecido com este:

Plaintext
//
// Use this file to mount additional paths to the filesystem
// DO NOT add a slash to the end of the filename
//

"mountcfg"
{
    // "cstrike"    "C:\steamcmd\steamapps\common\Counter-Strike Source\cstrike"
    // "tf"         "C:\mytf2server\tf"
}
Dentro das chaves { }, adicione uma nova linha para o Black Mesa. Certifique-se de não colocar as barras duplas (//) no início da sua linha, pois elas servem para comentar/desativar o código.

O formato deve ser: "nome_curto" "caminho_absoluto". Adicione a seguinte linha:

Plaintext
"bms"    "C:\Program Files (x86)\Steam\steamapps\common\Black Mesa\bms"
O seu arquivo final deve ficar parecido com isto:

Plaintext
"mountcfg"
{
    "bms"    "C:\Program Files (x86)\Steam\steamapps\common\Black Mesa\bms"
}
Salve o arquivo e feche o editor.

⚠️ Avisos Importantes de Compatibilidade
Embora o método acima faça com que o GMod leia os arquivos do Black Mesa, você vai encontrar problemas de renderização e física. A Crowbar Collective atualizou substancialmente a engine base do jogo (especialmente para a parte do Xen), criando incompatibilidades diretas com a versão da Source que o Garry's Mod utiliza.

Fique atento aos seguintes problemas conhecidos:

Iluminação e Shaders Quebrados: O Black Mesa usa um sistema de iluminação e renderização customizado (XEngine). Muitos materiais e texturas (especialmente do Xen) aparecerão com brilho exagerado, totalmente pretos, com reflexos de água corrompidos ou com a famosa textura quadriculada roxa e preta (Missing Texture), porque o GMod não consegue interpretar esses shaders avançados.

Bugs em Ragdolls e Física: O esqueleto (rig) e o sistema de colisões dos modelos do Black Mesa são diferentes do padrão do GMod. Se você tentar spawnar NPCs ou Ragdolls (como cientistas, guardas ou alienígenas), eles podem aparecer em "T-Pose", com membros retorcidos, ou afundando no chão devido à falta de compatibilidade dos hitboxes.

Mapas Incompatíveis: Carregar os mapas do Black Mesa (.bsp) diretamente no GMod causará crashes na maioria das vezes, ou o mapa carregará sem luz (fullbright), com sombras pretas sólidas e sem a maioria das partículas de ambiente (fogo, fumaça alienígena, etc).

Armas sem Animações C-Arms: As armas originais do Black Mesa não funcionarão perfeitamente na mão do seu jogador (viewmodel) nativamente no GMod sem o uso de addons de correção (fix addons) da Oficina (Workshop).

Dica de Especialista: Se o seu objetivo é apenas jogar com NPCs, armas ou mapas do Black Mesa no GMod, eu recomendo fortemente não fazer o mount manual pelo mount.cfg. Em vez disso, procure por addons de port ("Black Mesa NPCs", "Black Mesa Weapons", "Black Mesa Maps Fixed") na Steam Workshop do Garry's Mod. A comunidade já consertou os esqueletos, os materiais e os shaders nesses pacotes para rodarem nativamente na build atual do GMod.
