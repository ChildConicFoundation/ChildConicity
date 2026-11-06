---
title: 'ChildConicity: Quarterly iconicity analysis for CHILDES transcripts'
tags:
  - Python
  - child language
  - CHILDES
  - iconicity
  - corpus linguistics
authors:
  - name: Iban Rodriguez Iglesias
    affiliation: 1
    corresponding: true
  - name: ChildConic Foundation
    affiliation: 1
affiliations:
  - name: ChildConic Foundation
    index: 1
date: 6 November 2026
bibliography: paper.bib
---

# Summary

ChildConicity is a Python package for studying iconicity in early English with naturalistic transcripts from the Child Language Data Exchange System (CHILDES). Iconicity is the perceived resemblance between the form of a word and its meaning. A typical question is whether more iconic words appear earlier, or whether caregivers and children use them differently. Answering it requires the same transcripts grouped by age, split by speaker, and joined to a published rating of how iconic each word is. ChildConicity does that join.

The package reads CHAT transcripts (`.cha`), rewrites eleven North American English CHILDES corpora into one layout, and bins each recording by the child's age in quarters of a year. It then writes three related products. Token tables count words that appear in an iconicity-rating lexicon separately from words that do not. Type tables count lemmas by the grammatical category on the CHAT morphology tier. A rated export attaches the continuous iconicity rating, its standard deviation, the proportion of raters who knew the word, and the number of ratings. The same analysis runs from a desktop window, in English or Spanish, or from the command line. Corpora and ratings are downloaded by the user and are not stored in the software repository.

# Statement of need

Studies of iconicity in lexical development combine two public resources that were not built to be analyzed together. CHILDES distributes longitudinal parent–child recordings in CHAT format [@macwhinney2000]. A separate norming study provides iconicity ratings for more than 14,000 English words [@winter2023]. Linking them by hand means repairing corpus-specific folder layouts, parsing speaker codes and morphology tiers, binning ages, and matching spellings to the ratings table. Those steps are easy to repeat differently from one paper to the next.

General CHILDES tools already make the transcripts queryable. The CLAN programs distributed with CHILDES support a wide range of transcript analyses [@macwhinney2000]. `childes-db` mirrors CHILDES in a database with R and Python interfaces [@sanchez2019]. `PyLangAcq` reads CHAT files from Python [@lee2016]. None of these tools produces a quarterly iconicity table. A researcher can retrieve utterances with them and still has to write the age binning, the speaker split, the ratings join, and the export format.

ChildConicity is for developmental scientists and corpus linguists who want that table, and for students who need a guided path through the same steps. It is also for scripts: each stage is a command with explicit inputs, and a finished run writes a JSON file listing the files it created. The software contribution is the reproducible path from public CHAT corpora and the Winter ratings to speaker-specific quarterly counts. The package does not estimate a new iconicity scale, and it does not redistribute the corpora or the ratings.

# State of the field

CLAN remains the reference toolkit for CHAT. It is the right choice for analyses it already implements, including mean length of utterance, lexical diversity, and morphology searches. Extending CLAN with this iconicity workflow would tie a Python ratings join and a fixed set of corpus normalizers to a large program whose interface is the CLAN command language. ChildConicity calls no CLAN binary. It reads CHAT text directly so that the quarterly exports are ordinary JSON and CSV files.

`childes-db`, together with its Python interface `childespy`, is the better choice when the question is a custom query over many CHILDES corpora already loaded in the database [@sanchez2019]. That project versions the underlying transcripts. ChildConicity does not. `childes-db` also does not join utterances to the Winter iconicity norms, and it does not apply the corpus-by-corpus cleanup that several North American English collections need before their age and speaker metadata can be binned. Putting the iconicity export inside `childes-db` would make one database responsible for a ratings file that is versioned and published separately, and for normalizers that only some corpora need.

`PyLangAcq` is a general CHAT reader [@lee2016]. A thin script on top of it would still leave the hard part unsolved. The corpora supported here do not share one directory layout, or one way of recording the child's name and age, so the work that has to stay consistent is the per-corpus normalizer. Keeping those normalizers, the quarterly grouping, and the three export modes in one package makes the scientific workflow reviewable in one place. A reader library can replace the internal CHAT reader later without changing the exported tables.

The ratings come from Winter and colleagues, who asked speakers how much a word sounds like what it means and published the norms for reuse [@winter2023]. Earlier studies had related iconicity ratings to lexical category, age of acquisition, and differences between child and adult speech [@perry2015; @perry2017]. ChildConicity takes those results as the reason to build the pipeline. It does not repeat the norming study.

# Software design

Four choices organize the package.

Normalization is separate from analysis, and each corpus has its own normalizer. The eleven collections are Bates, Bloom, Brent, Brown, HSLLD, Kuczaj, New England, Post, Providence, Sachs, and Van Kleeck. Each normalizer writes a common layout in which the child's name and age are explicit metadata. A failed run writes into a pending directory and deletes that directory on error, so a half-written corpus does not replace the previous output. A twelfth corpus needs a new normalizer and tests. In return, the analysis code does not hide corpus quirks in scattered conditionals.

Age and speaker role are fixed before any iconicity count. Recordings are grouped into quarters of a year and labeled with the child's year and quarter, for example `02Y01Q`. Utterances are classified from CHAT participant roles into the target child, other children such as siblings or playmates, and adults. Quarterly groups also accumulate morpheme and utterance counts, so mean length of utterance can sit beside the word tables. Exports include all three speaker groups. Plots of grammatical types use the adult and target-child series.

In the token tables, "iconic" means that the ratings table contains the word. A word missing from that table is counted as non-iconic. The label answers whether the word was normed. It does not mean that the rating is above a theoretical cutoff. If the lowercase word occurs more than once in the ratings file, the kept row is the one with more ratings, then the higher proportion of raters who knew the word, then the higher rating. The rated export is where the continuous score is kept. Each lemma receives the rating, its standard deviation, the proportion known, and the number of ratings. Lemmas absent from the table receive empty values, and a study can apply its own threshold afterwards. Type counts can add the stored frequency of each lemma or count each distinct lemma entry once, and they can be limited to selected grammatical categories on the `%mor` tier.

The desktop window and the command line call the same functions. The window starts an analysis runner in a subprocess, and the runner writes a JSON summary of output paths. Scripts read that file instead of guessing where plots were saved. TalkBank downloads are the exception: they need a TalkBank account and a Chrome session. Credentials are read from environment variables, so they do not have to appear as command-line arguments. The ratings file is fetched from the Open Science Framework (`https://osf.io/ex37k/`) and is accepted only when the expected columns are present. Neither file is committed to the repository.

The implementation is ordinary Python. Tests cover the normalizers, the quarterly grouping, the ratings model, and the exporters. Continuous integration fails when coverage of `src` falls below 80 percent. The window layout, the plot helpers, and the runner entry point are outside that gate because they are thin shells around the tested functions. The package is released under the Boost Software License 1.0.

# Research impact statement

ChildConicity 1.0.8, released on 5 July 2026, is the first stable release of this pipeline. That release is archived on Zenodo (DOI `10.5281/zenodo.21199304`). The repository includes `CITATION.cff`, documentation in English and Spanish, and a test suite that GitHub Actions runs on every branch and pull request.

No independent paper is known to have used the package, and this statement does not report download counts: installation is from the source repository rather than from the Python Package Index. The concrete claim is narrower. Two users who run the same version on the same downloaded inputs obtain the same export layout for eleven public CHILDES corpora joined to the Winter ratings: quarterly token counts, grammatical type counts, and rated lemma tables. A methods section can point at that layout and at the archived version.

Authors who publish an analysis still cite the CHILDES corpus or corpora they used, following TalkBank's citation rules, and cite Winter and colleagues for the ratings [@macwhinney2000; @winter2023]. TalkBank asks authors to acknowledge grant NICHD HD082736 when they use CHILDES. Those citations belong to the data.

# AI usage disclosure

A generative AI coding assistant (Cursor, using the Grok model) drafted this manuscript from the repository's source, documentation, and citation metadata on 6 November 2026. It did not run the corpora, and it did not supply usage statistics. The submitting author has to check every claim against the source before submission. That check includes the iconic versus non-iconic split, the list of supported corpora, and the coverage exceptions. The repository does not record whether earlier versions of the software were written with generative AI tools. The author should add that fact here if it applies.

# Acknowledgements

ChildConicity depends on CHILDES and TalkBank for the transcripts and on the iconicity norms published by Winter and colleagues. No grant is recorded for the development of this software.

# References
