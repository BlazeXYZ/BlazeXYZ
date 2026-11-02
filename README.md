<div align="center">

<a href="https://blazexyz.com"><img src="assets/banner.svg" alt="BLAZE in dot lettering beside a black hole. QA, bug hunting, security tooling. I test things until they break, then help fix them." width="100%"></a>

<br>

[![website](https://img.shields.io/badge/blazexyz.com-0a070d?style=for-the-badge&logo=googlechrome&logoColor=db94ed)](https://blazexyz.com)
[![discord](https://img.shields.io/badge/discord-0a070d?style=for-the-badge&logo=discord&logoColor=db94ed)](https://discord.com/users/766780065198899210)
[![exypnos](https://img.shields.io/badge/exypnos_one-0a070d?style=for-the-badge&logoColor=db94ed)](https://exypnos.one/christian-block)

</div>

<img src="assets/divider.svg" alt="" width="100%">

```yaml
name:      Blaze
pronouns:  she / her
role:      Board member, Exypnos One Corp.
focus:     QA, bug hunting, counsel
building:  security tools for defenders · blazexyz.com · a Minecraft mod
likes:     dot art, black holes, shaders, web design, minecraft modding
```

## Security toolkit

Four small, dependency-free Python tools, each aimed at a different layer of defense. Each one goes past the obvious answer: an open port isn't a finding until you match it to a CVE, passing DMARC doesn't make an email safe, a strength meter's "entropy" is usually wrong, and a thousand failed logins matter less than the one that succeeded.

<div align="center">

<a href="https://github.com/BlazeXYZ/authtrail"><img src="assets/card-authtrail.svg" alt="authtrail: finds the one successful login hiding in thousands of failures, and what came next" width="49%"></a>
<a href="https://github.com/BlazeXYZ/mailsleuth"><img src="assets/card-mailsleuth.svg" alt="MailSleuth: phishing triage that catches business email compromise even when SPF, DKIM and DMARC pass" width="49%"></a>
<a href="https://github.com/BlazeXYZ/portscan-fingerprint"><img src="assets/card-portscan.svg" alt="portscan-fingerprint: async scanner that fingerprints services, reads TLS certificates and matches CVEs by CPE" width="49%"></a>
<a href="https://github.com/BlazeXYZ/pwaudit"><img src="assets/card-pwaudit.svg" alt="pwaudit: password strength by real guess cost, plus k-anonymity breach checks" width="49%"></a>

</div>

### One attack, four tools

Together they follow a single intrusion from start to finish:

```mermaid
%%{init: {"theme": "base", "themeVariables": {"primaryColor": "#0a070d", "primaryTextColor": "#f3ecf8", "primaryBorderColor": "#db94ed", "lineColor": "#db94ed", "fontFamily": "monospace"}}}%%
flowchart LR
    A["Phishing email<br><b>MailSleuth</b><br>is it phishing?"] --> B["Stolen or weak password<br><b>pwaudit</b><br>guessable? breached?"]
    B --> C["Exposed SSH service<br><b>portscan-fingerprint</b><br>what's open and vulnerable?"]
    C --> D["Login on the server<br><b>authtrail</b><br>did they get in? what next?"]
```

| Project | Layer | The interesting part | Status |
|---|---|---|---|
| [**authtrail**](https://github.com/BlazeXYZ/authtrail) | Host logs | Correlates a brute-forced login with the backdoor account and wiped logs that followed, as one incident timeline | [![tests](https://github.com/BlazeXYZ/authtrail/actions/workflows/tests.yml/badge.svg)](https://github.com/BlazeXYZ/authtrail/actions/workflows/tests.yml) |
| [**MailSleuth**](https://github.com/BlazeXYZ/mailsleuth) | Email | Flags a CEO-fraud email that passes SPF, DKIM *and* DMARC, because the attacker owns the lookalike domain | [![tests](https://github.com/BlazeXYZ/mailsleuth/actions/workflows/tests.yml/badge.svg)](https://github.com/BlazeXYZ/mailsleuth/actions/workflows/tests.yml) |
| [**portscan-fingerprint**](https://github.com/BlazeXYZ/portscan-fingerprint) | Network | CPE matching found 39 real CVEs for OpenSSH 8.2p1 where keyword search found 2; includes a hand-written X.509 parser | [![tests](https://github.com/BlazeXYZ/portscan-fingerprint/actions/workflows/tests.yml/badge.svg)](https://github.com/BlazeXYZ/portscan-fingerprint/actions/workflows/tests.yml) |
| [**pwaudit**](https://github.com/BlazeXYZ/pwaudit) | Credentials | Prices passwords by what an attacker would spend; breach checks send only 5 of 40 hash characters | [![tests](https://github.com/BlazeXYZ/pwaudit/actions/workflows/tests.yml/badge.svg)](https://github.com/BlazeXYZ/pwaudit/actions/workflows/tests.yml) |

<details>
<summary><b>What they have in common</b></summary>
<br>

- **Standard library only.** No `pip install`, no supply chain. Each tool includes its own parsers: DER certificates, syslog, email headers.
- **Hostile input is the default.** Scan banners, email headers and SSH usernames are all attacker-controlled. Every report is escaped and ships with no JavaScript.
- **Never falsely safe.** When a check can't run, the tool says "unavailable", never "clean".
- **Mapped to MITRE ATT&CK**, so findings come out in the vocabulary defenders already use.
- **Tested like they matter.** CI on Linux and Windows, plus regression tests for the real bugs found along the way, such as a BOM that made `password` look strong and a regex silently broken by a backspace byte.

</details>

## Also building

| | |
|---|---|
| 🌌 **[blazexyz.com](https://blazexyz.com)** | My site: a three.js black hole, galaxy and highway behind liquid-glass panels, with dot-matrix type and live Discord presence. Next.js, React Three Fiber, React Spring, custom GLSL. |
| ⛏️ **Shadow Slave** | A Fabric mod for Minecraft. |

## Tools I reach for

<div align="center">

![Python](https://img.shields.io/badge/python-0a070d?style=flat-square&logo=python&logoColor=db94ed)
![TypeScript](https://img.shields.io/badge/typescript-0a070d?style=flat-square&logo=typescript&logoColor=db94ed)
![Next.js](https://img.shields.io/badge/next.js-0a070d?style=flat-square&logo=nextdotjs&logoColor=db94ed)
![React](https://img.shields.io/badge/react-0a070d?style=flat-square&logo=react&logoColor=db94ed)
![three.js](https://img.shields.io/badge/three.js-0a070d?style=flat-square&logo=threedotjs&logoColor=db94ed)
![GLSL](https://img.shields.io/badge/glsl-0a070d?style=flat-square&logo=opengl&logoColor=db94ed)
![Java](https://img.shields.io/badge/java-0a070d?style=flat-square&logo=openjdk&logoColor=db94ed)
![GitHub Actions](https://img.shields.io/badge/github_actions-0a070d?style=flat-square&logo=githubactions&logoColor=db94ed)
![MITRE ATT&CK](https://img.shields.io/badge/mitre_att%26ck-0a070d?style=flat-square)

</div>

<img src="assets/divider.svg" alt="" width="100%">

<div align="center"><sub>Security tools here are for systems you own or are authorized to test.</sub></div>
