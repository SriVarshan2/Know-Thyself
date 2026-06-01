# NAMING MAP — short name → full meaning → category
# ses:session state   cor:correct   ttl:total   ovr:overconf  und:underconf
# cal:calibration     c1/c2/c3:confidence counts  log:result log list
# pmp:profile map     THR:threshold  qst:questions  q:current question
# hit:correct flag    ans:answer(0-based)  cnf:confidence(1-3)  kna:accuracy
# hk:high-know flag   oc:overconf flag  prf:profile tuple  grd:grade letter
# arr:arrow  lbl:label  res:result  nm:name  dsc:description  ins:insight
# pth:path  fh:file  ln:sep  hdr:banner  pmt:prompt  i:idx  o:option  skp:skipped
import json
import sys
import random

THR = 0.6
pmp = {
    (True, True): ("SHARP MIND", "Your confidence matched your knowledge. You know what you know and you know it.", "Keep identifying your weakest topics to maintain this edge."),
    (True, False): ("DOUBTER", "You knew more than you trusted yourself to know. Believe your preparation next time.", "Back yourself more. Your instincts are stronger than your confidence."),
    (False, True): ("OVERCLAIMER", "You walked into this quiz certain you knew the answers. The questions disagreed.", "Before your next exam, flag every topic you feel certain about and review it first."),
    (False, False): ("REALIST", "You were honest about the limits of your knowledge. Now go expand those limits.", "Your self-awareness is your foundation. Now build your knowledge on top of it."),
}


def load_qst(pth):
    try:
        with open(pth, encoding="utf-8") as fh: raw = json.load(fh)
        if not raw: print("Error: No questions loaded."); sys.exit(1)
        req = ('txt', 'opt', 'ans', 'why', 'top', 'dif')
        qst = [q for q in raw if all(k in q for k in req)]
        skp = len(raw) - len(qst)
        if skp: print(f"Warning: {skp} question(s) skipped (missing fields).")
        if not qst: print("Error: No valid questions found."); sys.exit(1)
        return qst
    except FileNotFoundError: print("Error: questions.json not found."); sys.exit(1)
    except json.JSONDecodeError: print("Error: questions.json is malformed."); sys.exit(1)


def get_cnf(pmt):
    while True:
        try:
            cnf = int(input(pmt))
            if 1 <= cnf <= 3: return cnf
            print("  Enter 1-3.")
        except (ValueError, EOFError): print("  Enter 1-3.")


def get_ans(q):
    print(f"\n{q['txt']}")
    for i, o in enumerate(q['opt']): print(f"  {i+1}. {o}")
    while True:
        try:
            ans = int(input("Answer [1-4]: ")) - 1
            if 0 <= ans <= 3: break
            print("  Enter 1-4.")
        except (ValueError, EOFError): print("  Enter 1-4.")
    return ans, get_cnf("Confidence? (1=Unsure  2=Fairly Sure  3=Certain): ")


def run_upd(ses, q, ans, cnf):
    hit = ans == q['ans']
    if hit: ses['cor'] += 1
    ses['ttl'] += 1; ses[['c1', 'c2', 'c3'][cnf - 1]] += 1
    lbl = ["Unsure", "Fairly Sure", "Certain"][cnf - 1]
    if hit and cnf == 1: ses['und'] += 1
    elif not hit and cnf == 3: ses['ovr'] += 1
    kna = ses['cor'] / ses['ttl']
    cal = 1.0 - (ses['ovr'] * 2 + ses['und']) / (ses['ttl'] * 2)
    arr = "^" if cal >= ses['cal'] else "v"
    ses['cal'] = cal
    print("✓ Correct!" if hit else f"✗ Wrong.\nWhy: {q['why']}")
    print(f"Cal:{cal*100:.1f}%{arr}  Know:{kna*100:.1f}%  [{lbl}]\n")
    ses['log'].append(("Correct" if hit else "Wrong", lbl))


def get_prf(ses):
    kna = ses['cor'] / ses['ttl']
    hk, oc = kna >= THR, ses['ovr'] >= ses['und']
    return pmp[(hk, oc)], kna


def show_rep(ses, prf, kna):
    ln, (nm, dsc, ins) = "=" * 54, prf
    cal = ses['cal'] * 100
    grd = next(g for t, g in [(90, "A"), (75, "B"), (60, "C"), (45, "D"), (0, "F")] if cal >= t)
    bia = ses['ovr'] / (ses['ovr'] + ses['und']) if (ses['ovr'] + ses['und']) > 0 else 0.5
    print(f"\n  --- Quiz Complete ---\n{ln}\n  KNOW THYSELF -- FINAL REPORT\n{ln}")
    print(f"  PERFORMANCE\n  Questions Answered : {ses['ttl']}\n  Correct Answers    : {ses['cor']}/{ses['ttl']} ({kna*100:.1f}%)")
    print(f"\n  CALIBRATION INTELLIGENCE\n  Calibration Score  : {cal:.1f}% (Grade: {grd})\n  Overconfident Qs   : {ses['ovr']}\n  Underconfident Qs  : {ses['und']}")
    print(f"  Confidence Bias    : {bia*100:.1f}% toward overconfidence")
    print(f"  Confidence Split   : Unsure {ses['c1']}  Fairly Sure {ses['c2']}  Certain {ses['c3']}")
    print(f"\n{ln}\n\n  YOUR LEARNER PROFILE : {nm}\n\n  {dsc}\n  {ins}\n\n{ln}")
    print("  Know what you know. Know what you only think you know.\n")


def main():
    qst = load_qst("questions.json")
    random.shuffle(qst)
    ses = {'cor': 0, 'ttl': 0, 'ovr': 0, 'und': 0, 'cal': 1.0, 'c1': 0, 'c2': 0, 'c3': 0, 'log': []}
    hdr = ("\n  +--------------------------------+\n  |   K N O W   T H Y S E L F    |\n  |  Know what you know.          |\n  |  Know what you only think     |\n  |  you know.                    |\n  +--------------------------------+")
    print(hdr)
    for idx, q in enumerate(qst):
        print(f"\n[Q{idx+1}/{len(qst)}] {q['top']} | {q['dif']}")
        ans, cnf = get_ans(q)
        run_upd(ses, q, ans, cnf)
    if ses['ttl'] == 0: print("No questions answered."); sys.exit(0)
    prf, kna = get_prf(ses)
    show_rep(ses, prf, kna)


if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print("\nSession ended."); sys.exit(0)
