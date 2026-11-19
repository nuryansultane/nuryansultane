"""Gera os painéis SVG do perfil: whoami.svg e contribuicoes.svg.

No GitHub Actions lê as contribuições reais pela API GraphQL (GITHUB_TOKEN).
Localmente aceita --dias ficheiro.json com {"AAAA-MM-DD": n}.
"""
import datetime as dt, json, os, sys, urllib.request
from html import escape

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, '..', 'assets')
LOGIN = os.environ.get('PERFIL_LOGIN', 'nuryansultane')
FONTE = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
C = dict(bg='#0a0b0f', jan='#0e1016', borda='#23262f', txt='#e6e8ef', fraco='#8b90a0', apagado='#4a4f60',
         acc='#4f6bff', acc2='#a9b6ff', ok='#3ecf8e')
ESCALA = ['#161a26', '#1d2a66', '#2c43c9', '#4f6bff', '#a9b6ff']
MESES = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']


def janela(w, h, titulo, corpo, estilo=''):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(titulo)}">
<style>
text{{font-family:{FONTE};fill:{C['txt']}}}
.f{{fill:{C['fraco']}}} .a{{fill:{C['acc2']}}} .k{{fill:{C['acc']}}} .ok{{fill:{C['ok']}}} .ap{{fill:{C['apagado']}}}
.cur{{animation:pisca 1s steps(1) infinite}} @keyframes pisca{{50%{{opacity:0}}}}
.ent{{opacity:0;animation:ent .5s ease forwards}} @keyframes ent{{to{{opacity:1}}}}
{estilo}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important;opacity:1!important}}}}
</style>
<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" fill="{C['jan']}" stroke="{C['borda']}"/>
<circle cx="20" cy="18" r="5" fill="#ff5f57"/><circle cx="37" cy="18" r="5" fill="#febc2e"/><circle cx="54" cy="18" r="5" fill="#28c840"/>
<text x="{w/2}" y="22" text-anchor="middle" font-size="11" class="f">{escape(titulo)}</text>
<line x1="0" y1="36" x2="{w}" y2="36" stroke="{C['borda']}"/>
{corpo}
</svg>'''


def prompt(x, y, comando, atraso=0.0, dur=0.9):
    """Linha 'nuryan@github ~ $ comando' com o comando a ser escrito."""
    n = len(comando)
    largura = n * 7.85
    cid = 'p' + ''.join(ch for ch in comando if ch.isalnum()) + str(int(y))
    return f'''<clipPath id="{cid}"><rect x="{x+150}" y="{y-13}" width="0" height="18"><animate attributeName="width" from="0" to="{largura+4}" begin="{atraso}s" dur="{dur}s" fill="freeze" calcMode="discrete" values="{';'.join(str(round(largura*i/n+0.5,1)) for i in range(n+1))}"/></rect></clipPath>
<text x="{x}" y="{y}" font-size="13"><tspan class="a">nuryan@github</tspan><tspan class="f"> ~ </tspan><tspan class="k">$</tspan></text>
<text x="{x+150}" y="{y}" font-size="13" clip-path="url(#{cid})">{escape(comando)}</text>'''


def whoami():
    import base64
    foto = base64.b64encode(open(os.path.join(AQUI, 'retrato-codigo.jpg'), 'rb').read()).decode()
    W, H = 860, 500
    rx, ry, rw, rh = 20, 84, 420, 372
    t0, td = 1.0, 2.2
    retrato = (f'<clipPath id="imprime"><rect x="{rx}" y="{ry}" width="{rw}" height="0">'
               f'<animate attributeName="height" from="0" to="{rh}" begin="{t0}s" dur="{td}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".4 0 .2 1"/></rect></clipPath>'
               f'<image x="{rx}" y="{ry}" width="{rw}" height="{rh}" href="data:image/jpeg;base64,{foto}" clip-path="url(#imprime)"/>'
               f'<rect x="{rx+20}" y="{ry}" width="{rw-40}" height="2" rx="1" fill="{C["acc2"]}" opacity="0">'
               f'<animate attributeName="y" from="{ry}" to="{ry+rh}" begin="{t0}s" dur="{td}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".4 0 .2 1"/>'
               f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.05;.9;1" begin="{t0}s" dur="{td}s" fill="freeze"/></rect>')
    info = [('', 'nuryan@github', 'a'), ('', '─' * 24, 'ap'),
            ('Nome', 'Nuryan Sultane', ''), ('Função', 'Programador full-stack', ''), ('Local', 'Moçambique', ''),
            ('Curso', 'Informática de Economia e Gestão', ''), ('', '4.º ano · em curso', 'f'), ('Stack', 'Laravel · React · TypeScript', ''),
            ('', 'Node.js · Tailwind · Python', ''), ('Dados', 'MariaDB · MySQL', ''), ('Integra', 'M-Pesa · APIs REST · Excel/CSV', ''),
            ('Projetos', 'nsERP · EduFuturo · nsEDU', ''), ('Site', 'nuryansultane.github.io', 'k'), ('Estado', 'disponível para projetos', 'ok')]
    ix, iy = 474, 104
    linhas = [retrato]
    blocos = []
    for i, (k, v, cls) in enumerate(info):
        y = iy + i * 22
        d = f'style="animation-delay:{1.4+i*.12:.2f}s"'
        if k:
            blocos.append(f'<text x="{ix}" y="{y}" font-size="13" class="ent" {d}><tspan class="a">{escape(k)}</tspan><tspan class="f">:</tspan><tspan x="{ix+78}" class="{cls}">{escape(v)}</tspan></text>')
        else:
            blocos.append(f'<text x="{ix+(78 if i>2 else 0)}" y="{y}" font-size="13" class="ent {cls}" {d}>{escape(v)}</text>')
    paleta = ''.join(f'<rect x="{ix+i*26}" y="{iy+len(info)*22-6}" width="22" height="12" rx="3" fill="{c}" class="ent" style="animation-delay:{3.2+i*.06:.2f}s"/>' for i, c in enumerate(ESCALA + [C['acc2'], C['ok'], '#febc2e']))
    corpo = prompt(26, 64, 'whoami') + '\n' + '\n'.join(linhas) + '\n' + '\n'.join(blocos) + paleta + \
        f'<text x="26" y="{H-18}" font-size="13" class="ent" style="animation-delay:3.6s"><tspan class="a">nuryan@github</tspan><tspan class="f"> ~ </tspan><tspan class="k">$</tspan><tspan class="cur" fill="{C["acc2"]}"> ▌</tspan></text>'
    return janela(W, H, 'nuryan@github: ~', corpo)


def contribuicoes_api():
    tok = os.environ.get('GITHUB_TOKEN')
    if not tok:
        return None
    q = '{"query":"query($l:String!){user(login:$l){contributionsCollection{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}","variables":{"l":"%s"}}' % LOGIN
    req = urllib.request.Request('https://api.github.com/graphql', data=q.encode(), headers={'Authorization': 'bearer ' + tok, 'Content-Type': 'application/json', 'User-Agent': 'perfil-painel'})
    data = json.load(urllib.request.urlopen(req, timeout=30))
    semanas = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
    return {d['date']: d['contributionCount'] for s in semanas for d in s['contributionDays']}


def contribuicoes(dias, hoje=None):
    hoje = hoje or dt.date.today()
    fim = hoje
    ini = fim - dt.timedelta(days=364)
    ini -= dt.timedelta(days=(ini.weekday() + 1) % 7)  # começa ao domingo, como o GitHub
    todos = [ini + dt.timedelta(days=i) for i in range((fim - ini).days + 1)]
    cont = [dias.get(d.isoformat(), 0) for d in todos]
    ano = [(d, c) for d, c in zip(todos, cont) if d > fim - dt.timedelta(days=365)]
    total = sum(c for _, c in ano)
    ativos = sum(1 for _, c in ano if c)
    melhor = max(ano, key=lambda x: x[1]) if ano else (hoje, 0)
    # sequências
    maior = seq = 0
    for _, c in ano:
        seq = seq + 1 if c else 0
        maior = max(maior, seq)
    atual = 0
    for d, c in reversed(ano):
        if c: atual += 1
        elif d == fim: continue
        else: break
    media = total / ativos if ativos else 0
    mx = max(cont) or 1
    nivel = lambda c: 0 if c == 0 else 1 if c <= mx * .25 else 2 if c <= mx * .5 else 3 if c <= mx * .75 else 4
    W, H = 860, 418
    x0, y0, cel, gap = 58, 104, 11, 3
    rects, rotulos, ultimo_mes = [], [], None
    for i, (d, c) in enumerate(zip(todos, cont)):
        col, lin = i // 7, (d.weekday() + 1) % 7
        x, y = x0 + col * (cel + gap), y0 + lin * (cel + gap)
        rects.append(f'<rect x="{x}" y="{y}" width="{cel}" height="{cel}" rx="2.5" fill="{ESCALA[nivel(c)]}" class="ent" style="animation-delay:{.9+col*.028:.3f}s"><title>{c} em {d.isoformat()}</title></rect>')
        if lin == 0 and d.month != ultimo_mes and d.day <= 7:
            ultimo_mes = d.month
            rotulos.append(f'<text x="{x}" y="{y0-10}" font-size="10.5" class="f">{MESES[d.month-1]}</text>')
    dias_sem = ''.join(f'<text x="{x0-30}" y="{y0+lin*(cel+gap)+9}" font-size="10" class="f">{t}</text>' for lin, t in [(1, 'seg'), (3, 'qua'), (5, 'sex')])
    legenda = ''.join(f'<rect x="{W-150+i*15}" y="{y0+7*(cel+gap)+10}" width="{cel}" height="{cel}" rx="2.5" fill="{c}"/>' for i, c in enumerate(ESCALA))
    yl = y0 + 7 * (cel + gap) + 20
    resumo = f'<text x="{x0}" y="{yl}" font-size="12" class="ent" style="animation-delay:2.2s"><tspan fill="{C["txt"]}" font-weight="700">{total}</tspan><tspan class="f"> contribuições no último ano</tspan></text>' + \
        f'<text x="{W-185}" y="{yl}" font-size="10" class="f">menos</text>{legenda}<text x="{W-72}" y="{yl}" font-size="10" class="f">mais</text>'
    cartoes = [('sequência atual', atual, 'dias'), ('maior sequência', maior, 'dias'), ('contribuições', total, 'último ano'),
               ('dias ativos', ativos, 'de 365'), ('melhor dia', melhor[1], melhor[0].strftime('%d/%m/%Y')), ('média', f'{media:.1f}', 'por dia ativo')]
    yc = yl + 22
    cw = (W - 2 * 26 - 5 * 10) / 6
    cards = []
    for i, (k, v, s) in enumerate(cartoes):
        x = 26 + i * (cw + 10)
        dl = f'style="animation-delay:{2.4+i*.1:.2f}s"'
        cards.append(f'<g class="ent" {dl}><rect x="{x:.1f}" y="{yc}" width="{cw:.1f}" height="70" rx="9" fill="{C["bg"]}" stroke="{C["borda"]}"/>'
                     f'<text x="{x+12:.1f}" y="{yc+20}" font-size="10" class="f">$ {escape(k)}</text>'
                     f'<text x="{x+12:.1f}" y="{yc+46}" font-size="22" font-weight="700" fill="{C["acc2"] if i in (0, 2) else C["txt"]}">{v}</text>'
                     f'<text x="{x+12:.1f}" y="{yc+61}" font-size="9.5" class="ap">{escape(s)}</text></g>')
    # barras por mês (últimos 12 meses)
    meses = []
    m = dt.date(fim.year, fim.month, 1)
    for _ in range(12):
        meses.append(m); m = (m - dt.timedelta(days=1)).replace(day=1)
    meses.reverse()
    soma = [sum(c for d, c in ano if d.year == mm.year and d.month == mm.month) for mm in meses]
    smx = max(soma) or 1
    yb, hb = yc + 140, 52
    bw = (W - 2 * 26 - 11 * 8) / 12
    barras = []
    for i, (mm, s_) in enumerate(zip(meses, soma)):
        x = 26 + i * (bw + 8); h = max(3, hb * s_ / smx)
        barras.append(f'<rect x="{x:.1f}" y="{yb-h:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="3" fill="{C["acc"] if s_ else ESCALA[0]}" style="transform-origin:{x+bw/2:.1f}px {yb}px;transform:scaleY(0);animation:cresce .8s cubic-bezier(.2,.8,.2,1) {3.0+i*.06:.2f}s forwards"/>'
                      f'<text x="{x+bw/2:.1f}" y="{yb+14}" font-size="9.5" text-anchor="middle" class="f">{MESES[mm.month-1]}</text>'
                      + (f'<text x="{x+bw/2:.1f}" y="{yb-h-5:.1f}" font-size="9.5" text-anchor="middle" class="a ent" style="animation-delay:{3.4+i*.06:.2f}s">{s_}</text>' if s_ else ''))
    corpo = prompt(26, 64, './contribuicoes.sh') + ''.join(rotulos) + dias_sem + ''.join(rects) + resumo + ''.join(cards) + \
        f'<text x="26" y="{yc+104}" font-size="13" class="ent" style="animation-delay:2.9s"><tspan class="a">nuryan@github</tspan><tspan class="f"> ~ </tspan><tspan class="k">$</tspan><tspan> ./atividade.sh --mensal</tspan></text>' + ''.join(barras)
    est = '@keyframes cresce{to{transform:scaleY(1)}}'
    return janela(W, H, 'contribuicoes.sh', corpo, est)



PROJETOS = [
    ('nserp', 'nsERP', 'Gestão empresarial', ['Vendas, reservas, facturação e stock,', 'pagamentos M-Pesa e loja online.'],
     ['Laravel', 'React', 'TS', 'MariaDB'], '41 tabelas · 90 ecrãs · 310+ testes', 'monografia · testado na LemServices', C['ok']),
    ('edufuturo', 'EduFuturo', 'Ensino online', ['Cursos em vídeo, exercícios e', 'certificados, em 4 línguas.'],
     ['Laravel', 'React', 'TS', 'PWA'], '32 ecrãs · 90+ testes · IA', 'projeto pessoal', C['acc2']),
    ('nsedu', 'nsEDU', 'Gestão académica', ['Matrículas, notas e pautas,', 'propinas e portal do estudante.'],
     ['Laravel', 'React', 'TS', 'MariaDB'], '37 tabelas · 41 ecrãs · 85+ testes', 'em desenvolvimento', '#febc2e'),
]


def projeto(chave, nome, tipo, desc, stack, numeros, estado, cor_estado, atraso=0.0):
    import base64
    foto = base64.b64encode(open(os.path.join(AQUI, 'capas', chave + '.jpg'), 'rb').read()).decode()
    W, H = 280, 318
    x0 = 14
    chips, cx = [], x0
    for t in stack:
        w = 12 + len(t) * 6.6
        chips.append(f'<rect x="{cx:.1f}" y="244" width="{w:.1f}" height="20" rx="10" fill="{C["bg"]}" stroke="{C["borda"]}"/><text x="{cx+w/2:.1f}" y="258" font-size="10" text-anchor="middle" class="f">{escape(t)}</text>')
        cx += w + 6
    corpo = (f'<g class="ent" style="animation-delay:{atraso+.2:.2f}s"><clipPath id="cap{chave}"><rect x="{x0}" y="48" width="{W-2*x0}" height="{(W-2*x0)*280/532:.1f}" rx="6"/></clipPath>'
             f'<image x="{x0}" y="48" width="{W-2*x0}" height="{(W-2*x0)*280/532:.1f}" href="data:image/jpeg;base64,{foto}" clip-path="url(#cap{chave})" preserveAspectRatio="xMidYMid slice"/>'
             f'<rect x="{x0}" y="48" width="{W-2*x0}" height="{(W-2*x0)*280/532:.1f}" rx="6" fill="none" stroke="{C["borda"]}"/></g>'
             f'<g class="ent" style="animation-delay:{atraso+.45:.2f}s"><text x="{x0}" y="{196}" font-size="17" font-weight="700">{escape(nome)}</text>'
             f'<text x="{W-x0}" y="{196}" font-size="10" text-anchor="end" class="f">{escape(tipo)}</text>'
             + ''.join(f'<text x="{x0}" y="{214+i*14}" font-size="10.5" class="f">{escape(l)}</text>' for i, l in enumerate(desc)) + '</g>'
             f'<g class="ent" style="animation-delay:{atraso+.65:.2f}s">' + ''.join(chips) +
             f'<text x="{x0}" y="284" font-size="10.5" class="a">{escape(numeros)}</text>'
             f'<circle cx="{x0+4}" cy="300" r="3.5" fill="{cor_estado}"/><text x="{x0+13}" y="303.5" font-size="10" class="ap">{escape(estado)}</text></g>')
    return janela(W, H, '~/projetos/' + chave, corpo)

if __name__ == '__main__':
    os.makedirs(SAIDA, exist_ok=True)
    dias = None
    if '--dias' in sys.argv:
        dias = json.load(open(sys.argv[sys.argv.index('--dias') + 1]))
    if dias is None:
        dias = contribuicoes_api()
    if dias is None:
        sys.exit('Sem dados: defina GITHUB_TOKEN ou use --dias ficheiro.json')
    open(os.path.join(SAIDA, 'whoami.svg'), 'w', encoding='utf-8').write(whoami())
    open(os.path.join(SAIDA, 'contribuicoes.svg'), 'w', encoding='utf-8').write(contribuicoes(dias))
    for i, p in enumerate(PROJETOS):
        open(os.path.join(SAIDA, 'projeto-' + p[0] + '.svg'), 'w', encoding='utf-8').write(projeto(*p, atraso=i * .25))
    print('painéis gerados:', sum(dias.values()), 'contribuições')
