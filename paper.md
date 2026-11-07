---
title: 'ChildConicity: Joining CHILDES transcripts to external word tables'
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
date: 7 November 2026
bibliography: paper.bib
---

# Summary

ChildConicity is a Python program under development for people who work with transcripts of child language. It reads CHAT files, the `.cha` format of the Child Language Data Exchange System (CHILDES), and writes tables that another program can analyze. The version described here downloads and normalizes eleven North American English corpora. The intention is to cover the rest of the English CHILDES collection and, after that, to add Spanish corpora. Neither of those stages is built.

A CHAT file already records the words, the speaker, and, on a morphology line called `%mor`, a grammatical category and a lemma. ChildConicity keeps that information, groups each recording by the child's age in quarters of a year, and attaches one external lexicon: published ratings of iconicity for English words. Iconicity is the perceived resemblance between the sound of a word and its meaning. The joined table is the result the program is meant to hand on. A few simple plots can be drawn from the same table, so a user can see whether a question looks worth pursuing. The plots are a first look. The study, if it continues, happens in another program.

# Statement of need

Work on early vocabulary often needs two facts in the same row. One fact comes from the recording: who spoke, at what age, which lemma, and which grammatical category. The other fact comes from a word list compiled outside CHILDES. Iconicity ratings are the first list this project attaches. A later version could attach other published lists to the same row. The current code loads only the iconicity file.

Doing the alignment by hand means repairing a different folder layout for each corpus, reading speaker codes, parsing the morphology line, binning age, and matching spellings. ChildConicity is being written to do that preparation for the corpora it already knows, and to stop once the table exists. The intended users are the author and other developmental researchers who want the joined file, including students who will open it in a spreadsheet or in their own analysis code. The ordinary way to use the program is to export that file and continue elsewhere.

The eleven corpora are Bates, Bloom, Brent, Brown, HSLLD, Kuczaj, New England, Post, Providence, Sachs, and Van Kleeck. They are a working subset of English CHILDES: each one has a normalizer in this repository. A corpus without a normalizer is outside the program. Spanish transcripts are a later goal. The program does not read them.

# State of the field

Three established tools already make CHILDES transcripts usable. CLAN, distributed with CHILDES, searches CHAT files and computes measures such as mean length of utterance [@macwhinney2000]. `childes-db` stores a large mirror of CHILDES in a database, with R and Python interfaces, and versions the transcripts it holds [@sanchez2019]. `PyLangAcq` reads CHAT from Python [@lee2016]. When the task is a query, or an analysis those projects already implement, they are the tools to use. ChildConicity also leaves transcript versioning to `childes-db`. It does not try to become a general CHAT workbench.

The gap this repository is filling is narrower, and it is only partly filled. The author needs an explicit path from a named list of corpora to a file in which the morphology line is already joined to an external lexicon. CLAN, `childes-db`, and `PyLangAcq` do not distribute the Winter iconicity ratings, and they do not include the per-corpus cleanup used here [@winter2023]. A general function that would attach any word table to every CHILDES corpus would belong in a project with wider coverage than this one. ChildConicity does not provide that function. It joins one ratings file, for eleven corpora, and it lays the row out with a lemma and a grammatical category so that a later lexicon could be matched in the same place.

Those ratings come from a study in which speakers judged how much an English word sounds like what it means [@winter2023]. Earlier studies related the judgments to lexical category, age of acquisition, and differences between child and adult speech [@perry2015; @perry2017]. That work is why iconicity is the first column added to the export. ChildConicity does not collect new ratings.

# Software design

The program is organized around the export. Plots and the window are there to help a user decide whether the export is worth taking further.

Normalization is separate for each corpus. The eleven collections do not share one folder layout, or one convention for the child's name and age, so the differences stay in a normalizer instead of in the analysis. Adding another English corpus, or a Spanish corpus later, means writing another normalizer and tests. A normalizer writes into a temporary directory and deletes that directory if the run fails, which keeps a failed pass from replacing the previous output. The input is the `.cha` transcript CHILDES already distributes. The program does not convert audio into text.

Grammatical categories are read from the `%mor` line. The program is not a tagger. A morphology code is split at the vertical bar into a category and a remainder, and the remainder is split into a lemma and any trailing features. The category is the code the transcript already carries. An utterance with no `%mor` line does not enter the grammatical export. Speaker codes separate the target child, other children (such as siblings or playmates), and adults. Age is stored as a year-and-quarter label, for example `02Y01Q`. Quarterly groups also keep morpheme and utterance totals, from which mean length of utterance can be reported beside the word counts. The columns that do not depend on iconicity are the quarter, the speaker group, the category, the lemma, and the count. A further word table would have to match one of those columns, most naturally the lemma. The exporter that performs a join today knows only the iconicity file.

That file is a CSV from the Open Science Framework (`https://osf.io/ex37k/`), accepted only when the expected columns are present. In the token export, a word is counted as iconic when the file contains it and as non-iconic when it does not. The label means that the word was in the norms. It does not mean that the rating passed a cutoff. If the same lowercase word occurs on more than one row, the program keeps the row with more ratings, then the higher proportion of raters who knew the word, then the higher rating. The rated export copies the rating, its standard deviation, the proportion known, and the number of ratings onto each lemma, and leaves those fields empty when the lemma is absent. A threshold, if the study needs one, belongs in the program that reads the export. Type counts can add the stored frequency of a lemma or count each distinct lemma entry once, and they can be limited to selected `%mor` categories.

Plots are optional and elementary. They summarize the joined counts, including iconic and non-iconic words by quarter for adults and the target child. Their role is to show whether a pattern is visible at all. The desktop window, in English or Spanish, and the command line call the same runner, which writes a JSON file listing the output paths. That file is the handoff to a script or to another application. Downloading corpora from TalkBank requires an account and a Chrome session. Credentials are read from environment variables. Corpora and the ratings file are not stored in the source repository.

Tests cover the normalizers, the age grouping, the ratings lookup, and the exporters. Continuous integration fails when coverage of `src` falls below 80 percent. The window, the plot helpers, and the runner entry point are outside that threshold. The license is the Boost Software License 1.0.

# Research impact statement

Version 1.0.8, dated 5 July 2026, is an archived snapshot of this unfinished program. The archive is on Zenodo (DOI `10.5281/zenodo.21199304`). The repository includes `CITATION.cff`, documentation in English and Spanish, and a test suite that GitHub Actions runs on every branch and pull request. No published study is known to depend on the package. It is installed from the source repository, so this statement does not report a download count.

With this snapshot a user can, for the eleven corpora named above, write quarterly token tables, lemma tables by grammatical category, and lemma tables with iconicity columns, and can draw a few exploratory plots. Those files are what another program would open. The remaining English corpora, Spanish corpora, and lexicons other than the iconicity ratings are planned work. They are not part of version 1.0.8.

An analysis published from the export still cites the CHILDES corpora that were used and the ratings paper [@macwhinney2000; @winter2023]. TalkBank asks authors to acknowledge grant NICHD HD082736 when they use CHILDES. Those citations belong to the data.

# AI usage disclosure

A generative AI coding assistant (Cursor, using the Grok model) drafted this manuscript on 6 November 2026 and revised it on 7 November 2026 after the author corrected its scope. The revision follows that correction. The program is in development. It currently reads `.cha` files for eleven English corpora. The ordinary product is an export for other programs. The plots are a preliminary check. Further English corpora, then Spanish corpora, are a plan. Other word tables are a possible later join, and only the iconicity file is joined now. The assistant did not run the corpora. The submitting author still has to confirm the text against the source before sending it to the journal. The repository does not record whether the software itself was written with generative AI tools.

# Acknowledgements

The transcripts come from CHILDES and TalkBank. The iconicity norms were published by Winter and colleagues. No grant is recorded for the development of this software.

# References
