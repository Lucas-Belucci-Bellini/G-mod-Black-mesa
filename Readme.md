# Guia Definitivo: Integração e Estabilização de Black Mesa no Garry's Mod (x86-64)

Montar os assets do Black Mesa (BMS) no Garry's Mod (GMod) é um desafio técnico considerável. O Black Mesa não é apenas um mod de Half-Life 2; ele roda em uma ramificação pesadamente customizada da Source Engine (frequentemente apelidada de **XEngine**), que implementou iluminação diferida, renderização de sombras em tempo real, shaders customizados e modificações estruturais em modelos (`.mdl`) e mapas (`.bsp`).

Para facilitar a sua configuração, fornecemos um script de automação neste repositório. Escolha o método que preferir para fazer a integração:

---

## ⚡ Método Automático (Recomendado)

O script detecta automaticamente os diretórios da Steam e configura o seu arquivo `mount.cfg` de forma segura, gerando backups preventivos para evitar corrupção de dados.

### Como Executar:
1. **Via Batch (Windows)**: Dê um duplo clique no arquivo [run.bat](file:///c:/G-mod-Black-mesa/run.bat).
2. **Via Terminal**: Rode o comando abaixo no terminal da pasta do projeto:
   ```bash
   python automate_mount.py
   ```
3. O script confirmará os caminhos detectados e criará um backup de segurança do seu `mount.cfg` antes de modificá-lo.

---

## 🛠️ Método Manual: Guia Passo a Passo

### 1. Montagem Absoluta (mount.cfg)
Para que o sistema de arquivos virtual da Source Engine (gerenciado pela classe `IFileSystem`) faça a busca de assets dentro do diretório do Black Mesa, precisamos configurar a montagem absoluta.

#### Passo A: Entender as dependências de Arquitetura (GMod x86-64)
O Garry's Mod em 32-bits possui um limite rígido de endereçamento virtual de 3,5 GB a 4 GB de RAM (limitação de processos de 32-bits). Como os assets do Black Mesa usam texturas de alta resolução e modelos complexos, tentar montá-los na versão padrão de 32-bits resultará inevitavelmente em crashes por exaustão de memória (**Out of Memory - OOM**) ao carregar mapas.

* **Ação**: Certifique-se de que a branch **x86-64 - Chromium + 64-bit binaries** está ativa na Steam (Propriedades do GMod > Betas > Selecionar a branch x86-64).

#### Passo B: Localização dos Diretórios
* **Caminho do Black Mesa (Origem)**: O que precisamos montar é a pasta `bms`, que contém os arquivos empacotados (`.vpk`) e estruturados do jogo.
  * Padrão: `C:\Program Files (x86)\Steam\steamapps\common\Black Mesa\bms`
* **Caminho do mount.cfg (Destino)**:
  * Padrão: `C:\Program Files (x86)\Steam\steamapps\common\GarrysMod\garrysmod\cfg\mount.cfg`

#### Passo C: Edição e Injeção de Caminho
Abra o arquivo `mount.cfg` e adicione o identificador `"bms"` apontando para a pasta absoluta. O arquivo deve ficar assim:

```keyvalues
"mountcfg"
{
    "bms"    "C:\Program Files (x86)\Steam\steamapps\common\Black Mesa\bms"
}
```

> [!IMPORTANT]
> **Nunca** adicione uma barra no final do caminho (ex: `bms\`). Isso invalida a resolução de diretórios da engine.

---

### 2. Usabilidade e Acesso ao Conteúdo
Apenas montar o jogo no `mount.cfg` não faz com que o menu do GMod saiba onde os arquivos estão localizados para spawnar. Para tornar os itens utilizáveis e corrigir erros visuais, siga este protocolo:

#### A. Criação de Spawnlists no Menu Q (Menu de Spawn)
O Garry's Mod lê listas de spawn organizadas a partir de arquivos `.txt` em `garrysmod/settings/spawnlist/`.

* **Para gerar essas listas manualmente**:
  1. No GMod, abra o Menu Q.
  2. Vá na aba **Browse** (Navegar) no canto inferior esquerdo.
  3. Clique em **Games** e procure por **Black Mesa**.
  4. Lá você poderá navegar pelas subpastas `models/` e criar spawnlists customizadas clicando com o botão direito nos modelos e selecionando "Add to spawnlist".
* **Alternativa de Desenvolvedor**: Existem scripts utilitários na comunidade que varrem a pasta `models/` do Black Mesa montado e geram arquivos `.txt` estruturados diretamente para a pasta de spawnlists do Garry's Mod.

#### B. Resolução de Texturas Rosas/Pretas (Missing Textures) e Shaders Quebrados
Muitos materiais do Black Mesa utilizam shaders exclusivos criados pela Crowbar Collective (como `BMS_Generic`, `BMS_Water`, `BMS_PostProcess` ou parâmetros como `$flowmap`). Quando o renderizador do GMod (que usa a ramificação clássica da Source Engine de Portal 2/CS:GO) encontra esses shaders no cabeçalho dos arquivos `.vmt` (Valve Material Type), ele não consegue compilá-los e reverte para a textura de erro rosa e preta.

##### Protocolo de Correção de Materiais:
Se você deseja portar um modelo ou textura específica e ela aparecer rosa:
1. Abra o arquivo `.vmt` correspondente em um editor de texto.
2. Localize a primeira linha (que define o shader). Geralmente estará algo como:
   ```vmt
   "BMS_Generic"
   ```
3. Substitua por um shader equivalente padrão da Source Engine compatível com o GMod:
   * Para props e modelos estáticos/dinâmicos: mude para `"VertexLitGeneric"`
   * Para texturas de superfícies de mapas (paredes, chão): mude para `"LightmappedGeneric"`
4. Remova parâmetros proprietários que causam aviso no console da engine, como diretivas específicas de iluminação física do Xen.

---

### 3. Protocolo de Resolução de Crashes (Crash to Desktop - CTD)
Este é o ponto de maior instabilidade. O Black Mesa carrega manifestos que colidem diretamente com a tabela de alocação de recursos do Garry's Mod.

#### A. Diagnóstico de Causas de Crash
Quando o GMod fecha repentinamente sem mensagem de erro, verifique a pasta `C:\Program Files (x86)\Steam\steamapps\common\GarrysMod\` em busca de arquivos `.mdmp` (Minidumps).

* **Crash na Tela de Carregamento**: Geralmente causado por conflito de manifestos de partículas ou scripts de som.
* **Crash ao Spawnar NPCs/Props**: Causado por estouro de limite de vértices na engine clássica, ou falta de ossos dinâmicos (`bones`) exigidos pela animação.
* **Crash ao Carregar Mapas (.bsp)**: A engine do Black Mesa grava mapas com cabeçalhos modificados (usando estruturas de dados exclusivas para o Xen). O renderizador de mapas do GMod tenta ler estruturas que não existem no seu parser padrão e fecha o processo instantaneamente.

#### B. Ações Práticas de Estabilização (Isolamento de Diretórios)
A engine da Source procura recursos em pastas prioritárias. Ao montar o Black Mesa, o GMod lerá arquivos de manifesto globais. Você **DEVE** remover ou renomear as seguintes pastas dentro do diretório do Black Mesa (`common/Black Mesa/bms/`) para evitar que elas sobrescrevam o núcleo do Garry's Mod:

* **Pasta `particles/` (Crítico)**:
  * **Problema**: O arquivo `particles/particles_manifest.txt` do Black Mesa substitui o manifesto de partículas do Garry's Mod. Quando o GMod tenta renderizar um efeito de física comum (como faíscas ou poeira) e não encontra a definição no manifesto corrompido, o jogo sofre um CTD imediato.
  * **Solução**: Vá até `common/Black Mesa/bms/` e renomeie a pasta `particles` para `_particles_backup`. (Isso impedirá que as partículas customizadas do BMS sejam montadas, mas salvará o GMod de crashes).
* **Pasta `scripts/` (Recomendado)**:
  * **Problema**: Contém scripts de armas, sons e manifestos de frases de NPCs que entram em conflito com as definições originais do GMod.
  * **Solução**: Renomeie a pasta `scripts` para `_scripts_backup`.
* **Pastas de Shaders/VFX**:
  * Se houver arquivos `.vcs` personalizados (compilados de shaders), eles podem confundir o renderizador do GMod. Certifique-se de que nenhum shader customizado esteja sobrescrevendo a pasta `shaders/` do GMod.

#### C. Parâmetros de Inicialização para Otimização
Clique com o botão direito no Garry's Mod na Steam > Propriedades > Geral > Opções de Inicialização, e adicione os seguintes parâmetros:

```bash
-systemalloc -heapsize 4194304 -mat_queue_mode 2 -gmod_mcore
```

* **`-systemalloc`**: Força a engine a usar o alocador de memória padrão do Windows (Heap do SO) em vez do alocador customizado da Valve (`MemAlloc`), melhorando drasticamente a paginação e estabilidade em 64-bits com grande volume de dados.
* **`-heapsize 4194304`**: Aloca 4 GB de memória cache do sistema dedicada para a engine Source (previne quedas de FPS por recarregamento constante de texturas).
* **`-mat_queue_mode 2`**: Força a renderização a rodar em uma fila multithreading paralela.
* **`-gmod_mcore`**: Habilita o suporte a múltiplos núcleos de processamento nativamente no GMod.

---

### 4. Avisos e Limitações Inevitáveis
Mesmo realizando toda a configuração perfeitamente, existem limitações da engine clássica da Source do Garry's Mod que impossibilitam a reprodução 100% fiel do Black Mesa.

* **Iluminação Quebrada (Fullbright / Black Lighting)**: O sistema de luzes do Black Mesa foi redesenhado para usar renderização diferida e mapas de iluminação estática avançados. Quando mapas do Black Mesa são abertos no Garry's Mod, eles perdem completamente o cálculo de sombras, carregando no modo *Fullbright* (iluminação máxima sem sombras) ou com sombras totalmente pretas que impossibilitam a visão.
* **Incompatibilidade Direta de Mapas (BMS BSP v20/v21)**: Você não conseguirá carregar a maioria dos mapas de Black Mesa (`.bsp`) diretamente no GMod sem que ocorra um crash. Especialmente os mapas do capítulo Xen, que usam texturas volumétricas, névoa dinâmica proprietária e contagem massiva de entidades. A única solução é baixar versões corrigidas ("Fixed for GMod") na Steam Workshop, onde modders recompilaram os mapas usando o compilador (`Hammer/VBSP`) clássico compatível com o GMod.
* **Ragdolls em Pose T / Limbos Físicos**: Os esqueletos (`skeleton rigs`) dos cientistas, guardas e criaturas do Black Mesa utilizam estruturas de ossos diferentes da versão original de Half-Life 2 (usada como base no Garry's Mod). Se você tentar spawnar um modelo original do BMS usando ferramentas físicas do GMod, as colisões (`hitboxes`) estarão ausentes ou deslocadas, resultando em personagens presos em Pose T, deformações corporais bizarras (membros esticando ao infinito) ou ragdolls atravessando o chão.
* **Animações de Braços (C_arms) Invisíveis nas Armas**: As armas originais do Black Mesa montadas nativamente não mapeiam os braços do jogador do GMod. Ao equipá-las, as mãos do jogador ficarão invisíveis, os modelos de visualização (`viewmodels`) estarão mal posicionados na tela ou não exibirão animações de recarga.

---

> [!TIP]
> **Recomendação de Veterano**: Para obter a melhor experiência com conteúdo de Black Mesa no Garry's Mod sem comprometer a estabilidade do seu jogo, utilize a montagem automática apenas para puxar *props* estáticos (como computadores, mobília e destroços industriais, que funcionam perfeitamente). Para NPCs, armas funcionais e mapas jogáveis, dê preferência aos **ports otimizados da Steam Workshop**, pois os autores desses pacotes já realizaram a correção de esqueletos, recompilação de shaders e otimização de materiais necessários para rodar na build atual do GMod.
