[![make.fun](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/Arik2779/the-passport-page-of-a-countr-2-20261121-0318/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/Arik2779/the-passport-page-of-a-countr-2-20261121-0318/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)

# The Passport Page of a Country That Isn't There

Entry for the [make.fun bounty](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318):
a deterministic, stdlib-only Python program that draws one open passport
spread for a country that does not exist and writes it to
`/output/entry.png`.

## The invented country

**The Republic of Valdoria** — a small landlocked mountain republic, capital
**Tarnova**, language Valdorian/English, currency the koruna (VK), coat of
arms a chamois over mountain peaks. Its neighbours are Kestrelia and Dunvar.

## The document

- **Holder:** Mara Ilves, born 14 Mar 1992 in Tarnova. Passport **VLD 482 913**,
  issued 03 Feb 2025, expires 03 Feb 2035. Stylised flat-colour portrait,
  holder's signature, and a machine-readable strip (MRZ) with real ICAO
  check digits.
- **Travel history** (every stamp dated after the 03 Feb 2025 issue):
  18 Apr 2025 departs Valdoria (Tarnova Intl) and arrives in Kestrelia;
  02 May 2025 departs Kestrelia; 03 May 2025 arrives in Dunvar (Sareen) on a
  type-C single-entry visa issued in Tarnova on 10 Apr 2025, valid until
  10 Jul 2025, employment prohibited; 17 May 2025 departs Dunvar and arrives
  home in Valdoria.
- **Telling detail:** an "Alpine transit fee — 15 VK, paid" stamp, and the
  printed note that the mountain passes are closed 01 Nov – 31 Mar and the
  passport must be carried at all times in the border zone.

## Run it

```sh
python3 main.py            # writes /output/entry.png
```

No dependencies, no network. The output is byte-identical on every run:
1024×704 px, ~20 KB PNG.

## Repository

`Arik2779/the-passport-page-of-a-countr-2-20261121-0318`
