# Tax and corporate-law review of commit `f26653b`

**Repository:** `/Volumes/SSD/code/personal/craftsman-marketplace`  
**Commit reviewed:** `f26653bda37a77768b2b5323a61ed2921ba64ae7`  
**Review date:** 2026-09-04  
**Scope:** The commit diff, read from the pinned commit with `git show`; later commits and working-tree changes were excluded.

This is a practitioner-facing technical review of a public drafting/workpaper skill. It is not a tax opinion or legal advice for any taxpayer or corporation. The reported defects are statements that should be corrected before practitioners are asked to rely on the skill.

## Executive conclusion

The commit is **not ready for publication**. The central PHC-before-AET ordering is correct, and the June-30 transition dates, the basic demand-loan/term-loan distinction, the information-return threshold change, the Form 8233 rule, and the S-corporation three-year termination rule are substantially correct. But the commit also introduces several categorical propositions that primary authority contradicts:

- it makes a signed accountable-plan instrument a federal tax prerequisite when the IRS expressly says a plan need not be written;
- it says a stock-consideration determination must be a separate signed instrument even though the MBCA comment says the opposite and DGCL §152 permits the determination in the issuance resolution;
- it says one false/backdated document automatically forfeits §6664(c) relief for every other item, although the statute applies by “portion” of an underpayment;
- it says fairness is the only route whenever the approving person is interested, ignoring disinterested-stockholder routes;
- it ships generic stock-closing templates with tax conclusions and evidence states already marked satisfied/verified, plus a Washington capacity rule under a `REPLACE-STATE` jurisdiction; and
- it cites current §6072(b) for the C-corporation return deadline even though current §6072(b) covers partnerships and S corporations.

I found no taxpayer-specific names, addresses, EINs, SSNs, account numbers, email addresses, or phone numbers in the added taxcraft material. The Washington and Delaware names in evaluation fixtures are synthetic test facts. The Washington citation in the production stock-audit template is nevertheless an improper jurisdiction hard-code, addressed below.

## Findings

### 1. HIGH — Federal accountable-plan status is made to depend on a signed instrument

**Locations:** `plugins/taxcraft/skills/tax/scenarios/accountable-plan.md:414-423`; `plugins/taxcraft/skills/tax/scenarios/pre-formation-binder.md:102-106`

**Exact quote:**

> “An unsigned plan is not an arrangement in force, and its effective date cannot precede its execution. A drafted-but-unexecuted plan, a plan approved in a consent nobody signed, and a plan resolution executed before the entity legally existed are all the same thing for this purpose: no arrangement.”

> “an accountable plan is effective only on execution by a body with authority to adopt it”

**Why this is wrong:** IRC §62(c) and Reg. §1.62-2 ask whether a reimbursement or expense-allowance **arrangement** has business connection, substantiation, and return-of-excess requirements. They do not require a written plan, a signature, or a board resolution as a condition of federal accountable-plan treatment. IRS Publication 5137 states expressly that an allowance or reimbursement policy, “not necessarily a written plan,” can qualify. A signature may be required by applicable entity law or internal governance and is valuable evidence, but the absence of a signed plan does not categorically prove that no tax arrangement existed. The commit itself correctly says at lines 427-432 that pre-incurrence written adoption is not a statutory element; the quoted rule contradicts that statement.

The annual-cycle statement at lines 177-182 is also too absolute. An annual-only process normally leaves older claims outside the fixed-date safe harbor and does not satisfy the quarterly-statement safe harbor, but an expense substantiated within 60 days can still be inside the fixed-date safe harbor even if the employer describes its general cycle as annual. Items outside a safe harbor remain subject to the regulation’s facts-and-circumstances reasonable-period test.

**Primary sources:** [IRC §62(c)](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A62+edition%3Aprelim%29); [Reg. §1.62-2](https://www.ecfr.gov/current/title-26/section-1.62-2); [IRS Publication 5137](https://www.irs.gov/pub/irs-pdf/p5137.pdf); [Rev. Rul. 2012-25](https://www.irs.gov/irb/2012-37_IRB).

**Replacement:**

> Federal accountable-plan treatment does not depend on a written or signed plan. Determine what reimbursement arrangement actually existed when the payment was made and whether it required business connection, timely substantiation, and return of excess under Reg. §1.62-2. A signed, prospectively adopted plan is preferred evidence and may be required by applicable entity law or internal governance, but do not treat a missing signature as conclusive that no federal tax arrangement existed. Never backdate an instrument. For timing, test each advance, substantiation, and excess return separately under the 30/60/120-day fixed-date safe harbors or the quarterly-statement safe harbor; items outside those safe harbors require a documented facts-and-circumstances reasonable-period analysis.

### 2. HIGH — The stock-adequacy rule invents a separate-instrument requirement and excludes lawful deferred consideration

**Locations:** `plugins/taxcraft/skills/tax/scenarios/stock-issuance.md:203-218`; `plugins/taxcraft/skills/tax/templates/adequacy-and-fairness-determination.md.template:13-14,51-56`

**Exact quotes:**

> “The adequacy determination is its own signed instrument, made before the issuance it supports. A recital inside the issuance resolution that the consideration ‘is adequate’ is not the determination.”

> “Do not sign it after the shares are issued, and do not replace it with a recital inside the issuance resolution.”

> “No certificate is to be delivered and no ledger entry made until ... the consideration ... is actually received.”

**Why this is wrong:** The official MBCA §6.21 comment says the board need not make an explicit adequacy determination by formal resolution; it may be inferred from authorization of shares for specified consideration. DGCL §152(a) expressly permits the numbers, times, and consideration to be set forth in a board resolution, and §152(d) makes the directors’ valuation judgment conclusive absent actual fraud. Neither authority requires a separate instrument. The same template also allows a “written promise” as consideration but then prohibits issuance until consideration is received. MBCA §6.21(b), (e) permits promissory notes and contracts for future services or benefits, with escrow or transfer restrictions; DGCL §156 permits partly paid shares. Formation-state law and the charter control.

**Primary sources:** [current MBCA resource and official text](https://www.americanbar.org/groups/business_law/resources/model-business-corporation-act/); [MBCA §6.21 official text/comment PDF](https://www.americanbar.org/content/dam/aba/administrative/business_law/corplaws/2016_mbca.authcheckdam.pdf); [DGCL §§152 and 156](https://delcode.delaware.gov/title8/c001/sc05/).

**Replacement:**

> Before issuance, document the authorized decision-maker’s good-faith determination that the specified consideration is adequate under the verified formation-state statute and the charter. The determination may appear in the issuance resolution or in a separate contemporaneous instrument; use a separate instrument only as an evidentiary preference, not as a universal legal requirement. If the consideration includes a promissory note, future services, or another deferred benefit, determine whether formation-state law permits the issuance and what escrow, transfer restriction, partly-paid-share notation, or other protection is required. Do not label shares fully paid and nonassessable before the governing statute permits that status.

### 3. HIGH — The generic stock templates are “green by default” and contain a live Washington rule

**Locations:** `plugins/taxcraft/skills/tax/templates/stock-issuance-audit.json.template:36-38,87-122`; `plugins/taxcraft/skills/tax/templates/stock-issuance-closing-manifest.json.template:23-49,52-58`; `plugins/taxcraft/skills/tax/schemas/stock-issuance-audit.schema.json:92-120,152-167`; `plugins/taxcraft/skills/tax/schemas/stock-issuance-closing-manifest.schema.json:33-104`; `plugins/taxcraft/skills/tax/evals/validate_corporate_records.py:229-239,344-453`

**Exact quotes:**

> `"capacity_authority_url": "https://app.leg.wa.gov/RCW/default.aspx?cite=23B.06.310"`

> `"section_351": "ISSUANCE_PRONGS_VERIFIED"`

> `"section_1202": "ISSUANCE_DATE_PRONGS_SATISFIED_PROVISIONAL"`

> `"section_1244": "ISSUANCE_DATE_PRONGS_SATISFIED_PROVISIONAL"`

> `"section_351_control_test_status": "SATISFIED"`

> `"verification_status": "VERIFIED"` and `"signature_method": "CRYPTOGRAPHIC_VALIDATED"`

**Why this is wrong:** A public blank template should not pre-assert tax qualification, counsel review, securities clearance, cryptographic signature validation, or evidence verification. Those conclusions require transaction facts and evidence. Section 351 requires qualifying property transferors to control the corporation immediately after the exchange; §§1202 and 1244 have many additional issuance-date and later tests. A user replacing names, dates, and hashes can easily leave the preselected conclusions in place. The schemas compound the problem by making several evidence and authority statuses `const: VERIFIED`, so the model cannot represent an incomplete closing in those fields.

The production template also declares the issuer jurisdiction as `REPLACE-STATE` while hard-coding Washington’s reacquired-share rule and URL. The validator checks only that the source hostname ends in `.gov`; it does not prove that the cited law belongs to the issuer’s formation jurisdiction. It can therefore accept a Washington rule for a Delaware or other-state corporation.

**Primary sources:** [IRC §351](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A351+edition%3Aprelim%29); [IRC §1202](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A1202+edition%3Aprelim%29); [IRC §1244](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A1244+edition%3Aprelim%29); [Washington RCW 23B.06.310](https://app.leg.wa.gov/RCW/default.aspx?cite=23B.06.310); [DGCL §§152-156, showing a different statutory framework](https://delcode.delaware.gov/title8/c001/sc05/).

**Replacement:**

```json
"formation_state_capacity_rule": "COUNSEL_VALIDATED_JURISDICTION_RULE",
"capacity_authority_url": "https://example.invalid/replace-with-official-formation-state-source",
"capacity_authority_verified_at": "2000-01-01T00:00:00Z",
"tax_positions": {
  "section_83": "UNVERIFIED",
  "section_351": "UNVERIFIED",
  "section_1202": "UNVERIFIED",
  "section_1244": "UNVERIFIED"
},
"section_351_control_percent_after": null,
"section_351_control_test_status": "COUNSEL_HOLD"
```

> Change the authority/evidence schemas to permit `UNVERIFIED` and `COUNSEL_HOLD`; make those the template defaults. A reconciled result may become `VERIFIED` only after evidence, authority, jurisdiction, date, and reviewer identity have been populated. Reject placeholder domains and reject a capacity source unless it is explicitly mapped to the issuer’s formation jurisdiction.

### 4. HIGH — The backdating warning states automatic civil and criminal consequences that the cited laws do not create

**Location:** `plugins/taxcraft/skills/tax/governance.md:459-466`

**Exact quotes:**

> “A backdated instrument produced to the IRS ... converts a late-documentation problem into a false-document problem (§7206; 18 U.S.C. §1001).”

> “It forfeits the §6664(c) reasonable-cause defense the entity will need for every other open item in the same file.”

**Why this is wrong:** Backdating is dangerous and should be prohibited, but the consequences are not automatic. Section 7206 requires the applicable statutory elements, including willfulness and material falsity; §7206(1) also concerns a document subscribed under penalties of perjury, while §7206(2) concerns willful assistance with a materially false document in a tax matter. 18 U.S.C. §1001 requires a knowing and willful materially false statement, concealment, or false document in a matter within federal jurisdiction. Section 6664(c) is explicitly applied to each **portion** of an underpayment, and Reg. §1.6664-4 requires a case-by-case facts-and-circumstances analysis. A false document can be devastating evidence of bad faith, especially for related items, but it does not legislatively forfeit reasonable-cause relief for every unrelated item in the file.

**Primary sources:** [IRC §7206](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A7206+edition%3Aprelim%29); [18 U.S.C. §1001](https://uscode.house.gov/view.xhtml?req=%28title%3A18+section%3A1001+edition%3Aprelim%29); [IRC §6664(c)](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A6664+edition%3Aprelim%29); [Reg. §1.6664-4](https://www.ecfr.gov/current/title-26/section-1.6664-4).

**Replacement:**

> A knowingly false or backdated instrument submitted in a federal tax matter may create criminal exposure under IRC §7206 or 18 U.S.C. §1001 when the statute’s jurisdictional, knowledge, willfulness, and materiality elements are met. It is also powerful evidence against reasonable cause and good faith under §6664(c), particularly for the portion of an underpayment and the factual issues to which the document relates. Section 6664(c) remains a portion-by-portion, facts-and-circumstances inquiry; do not state that one document automatically forfeits relief for unrelated items.

### 5. HIGH — The related-party policy wrongly says fairness is the only available approval route

**Locations:** `plugins/taxcraft/skills/tax/templates/related-party-transaction-policy.md.template:29-33`; `plugins/taxcraft/skills/tax/templates/adequacy-and-fairness-determination.md.template:41-49`

**Exact quote:**

> “Where the approving person is also the interested person, the disinterested-approval safe harbors are unavailable and fairness to the Entity is the only route.”

> “The safe harbors are unavailable because <e.g. the only director is the interested person>. Fairness to the Corporation is therefore the only route...”

**Why this is wrong:** The interested person’s inability to supply disinterested approval does not eliminate approval by other disinterested directors or by disinterested/qualified shares. Current DGCL §144(a) provides alternatives including disinterested-board approval, informed disinterested-stockholder approval, or fairness. The MBCA likewise provides qualified-director and qualified-share routes in addition to fairness. The template’s own adequacy document recognizes qualified-share approval, making the two templates internally inconsistent.

**Primary sources:** [current DGCL §144](https://delcode.delaware.gov/title8/c001/sc04/); [current MBCA resource, including §§8.61-8.63](https://www.americanbar.org/groups/business_law/resources/model-business-corporation-act/).

**Replacement:**

> Identify the formation-state conflict statute and the interested person’s role. Determine separately whether the transaction can be authorized by qualified/disinterested directors, approved or ratified by informed qualified/disinterested shares, or sustained as fair to the entity under the applicable statute. The interested person’s participation does not by itself eliminate every disinterested approval route. Record disclosure, voting eligibility, approval mechanics, and fairness facts required by the verified jurisdiction-specific rule.

### 6. MEDIUM — The C-corporation return deadline is attributed to the wrong current Code subsection

**Locations:** `plugins/taxcraft/skills/tax/entities/c-corp.md:218-220`; `plugins/taxcraft/skills/tax/templates/compliance-calendar.md.template:18-19`

**Exact quotes:**

> “Form 1120 due (§6072(b)): 15th day of the 4th month...”

> “§6072(b) — 15th day of the 4th month after year end; the June-30 exception applies...”

> “the general rule gives a deadline two weeks late.”

**Why this is wrong:** Current IRC §6072(a), not §6072(b), contains the general fourth-month income-tax-return rule. Current §6072(b) covers partnership and S-corporation returns. The June-30 transition is an effective-date rule in Pub. L. 114-41 §2006(a)(3)(B), not a current-text exception in §6072(b). The substantive transition is otherwise right: a June-30 C corporation with a tax year beginning before January 1, 2026 has a September 15 original deadline and a seven-month Form 7004 extension; for tax years beginning in 2026 the general fourth-month/six-month regime applies. October 15 is one month, not two weeks, after September 15.

**Primary sources:** [current IRC §6072](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A6072+edition%3Aprelim%29); [Pub. L. 114-41 §2006](https://www.govinfo.gov/content/pkg/PLAW-114publ41/pdf/PLAW-114publ41.pdf); [2026 IRS Publication 509](https://www.irs.gov/publications/p509); [2025 Form 7004 Instructions](https://www.irs.gov/instructions/i7004).

**Replacement:**

> **Form 1120 due:** Under current IRC §6072(a), generally the 15th day of the fourth month after year end; a calendar-year corporation is due April 15. Pub. L. 114-41 §2006 preserves the prior third-month deadline for a C corporation with a tax year ending June 30 and beginning before January 1, 2026: September 15, with a seven-month Form 7004 extension. For a tax year beginning in 2026, apply the general fourth-month deadline and six-month extension. The general rule would put the unextended June-30 deadline one month late, on October 15.

### 7. MEDIUM — The PHC summary uses the wrong inequality and understates the mechanics of both dividend cures

**Locations:** `plugins/taxcraft/skills/tax/entities/c-corp.md:77`; `plugins/taxcraft/skills/tax/scenarios/ccorp-tax-reduction.md:98-140`

**Exact quotes:**

> “PHC income > 60% of adjusted ordinary gross income”

> “subject to strict timing (generally 90 days from the determination) and a Form 976 claim.”

> “Ordinary planning is a consent dividend (§565) or an actual distribution...”

**Why this is wrong or incomplete:** Section 542(a)(1) uses **at least 60%**, not more than 60%. The detailed scenario correctly says `≥ 60%`, so the public skill is internally inconsistent at the boundary. The ordering rule is correct: §532(b)(1) excludes a PHC from AET, so PHC status should be tested before a §531 business-needs workpaper. The §533(a) preponderance burden statement is also correct.

For §547, the distribution must occur within 90 days after the determination and **before** Form 976 is filed; Form 976 must be filed within 120 days after the determination. The deduction does not reduce interest, additional amounts, or assessable penalties computed with respect to the PHC tax. For §565, a holder of consent stock on the last day of the corporation’s tax year must agree in a consent filed with the corporation’s return; the amount is deemed distributed in money and recontributed to capital on the last day, and the shareholder must account for the deemed dividend. Calling it merely “ordinary planning” omits the shareholder-level tax and filing mechanics.

**Primary sources:** [IRC §532](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A532+edition%3Aprelim%29); [IRC §533](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A533+edition%3Aprelim%29); [IRC §542](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A542+edition%3Aprelim%29); [IRC §547](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A547+edition%3Aprelim%29); [Form 976 and instructions](https://www.irs.gov/forms-pubs/about-form-976); [IRC §565](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A565+edition%3Aprelim%29).

**Replacement:**

> Personal holding company tax (§541) applies only after both §542 tests are run: personal holding company income is **at least 60%** of adjusted ordinary gross income, and more than 50% in value is owned, directly or through §544 attribution, by five or fewer individuals at some time during the last half of the year. Test §542 first because §532(b)(1) excludes a PHC from §531. A §547 deficiency dividend must be distributed within 90 days after the determination and before the Form 976 claim, which must be filed within 120 days; the deduction does not eliminate related interest, additional amounts, or assessable penalties. A §565 consent dividend requires eligible last-day consent-stock holders to file the prescribed consents with the corporate return; it is deemed distributed and recontributed on the last day and can create shareholder-level dividend tax despite no cash distribution.

### 8. MEDIUM — The §7872/§1274 relationship is misstated and the de minimis description is unsupported

**Location:** `plugins/taxcraft/skills/tax/scenarios/ccorp-tax-reduction.md:169-188`

**Exact quotes:**

> “priced under ... §7872, not under §1274(d). §1274(d) is the provision that publishes the applicable federal rates; it governs debt issued for property.”

> “The de minimis exceptions in §7872(c) are narrow and do not apply to most owner loans.”

**Why this is wrong or misleading:** Section 7872 is the operative below-market-loan rule for covered corporation-shareholder cash loans, but §7872(f)(2) expressly imports the applicable federal rate determined under §1274(d). Section 1274 as a whole governs the issue price of certain debt instruments issued for property; subsection (d) defines/determines the AFR framework. It does not itself “publish” rates. Treasury/IRS determines and publishes them monthly.

The demand/term distinction is substantially right but should describe the different statutory mechanics. A demand loan generally produces annual foregone-interest transfers, normally on the last day of each calendar year, using the short-term AFR applicable for the period. A below-market term loan is tested at inception by present value; the excess is deemed transferred at issuance and the deemed OID/interest consequences then run over the term, subject to later modification rules. Section 7872(c)(3) supplies a concrete $10,000 aggregate exception for certain compensation-related and corporate-shareholder loans, unless tax avoidance is a principal purpose. Whether it covers “most” owner loans is an unsupported empirical claim.

**Primary sources:** [IRC §7872](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A7872+edition%3Aprelim%29); [IRC §1274, including subsection (d)](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A1274+edition%3Aprelim%29); [IRS AFR rulings](https://www.irs.gov/applicable-federal-rates).

**Replacement:**

> Apply §7872 to a covered below-market corporation-shareholder cash loan; §7872(f)(2) determines the relevant AFR by reference to §1274(d). Section 1274 generally addresses issue price for certain debt issued for property, while §1274(d) supplies the AFR definitions used by §7872 and other provisions. For a demand loan, compute foregone interest for each calendar-year period using the applicable short-term AFR and treat the transfer/retransfer as occurring at year end unless regulations provide otherwise. For a term loan, test present value when the loan is made, treat the statutory excess as transferred at inception, and account for the resulting OID/interest over the term; retest a later significant modification as applicable. Separately test the §7872(c)(3) $10,000 aggregate exception and its principal-purpose tax-avoidance limitation rather than assuming it does or does not apply.

### 9. MEDIUM — The constructive-wage discussion conflates employee status with the existence of wages

**Location:** `plugins/taxcraft/skills/tax/scenarios/ccorp-tax-reduction.md:208-216`

**Exact quote:**

> “The reasonable-compensation cases and §3121(d)(1)/Reg. §31.3121(d)-1(b) reach an officer who performs more than minor services and receives remuneration.”

**Why this is misleading:** The core conclusion—services without remuneration do not, by nonpayment alone, create a fictional wage payment—is sound. But §3121(d)(1) generally makes a corporate officer an employee. The regulatory exception applies only when the officer performs no or only minor services **and** neither receives nor is entitled to receive remuneration. Thus, an officer performing substantial services remains an employee even if no wage has yet been paid. Wages still require remuneration actually or constructively paid; other payments, including distributions or purported loans, may be recharacterized as remuneration. The commit should keep those two questions separate.

**Primary sources:** [IRC §3121(d)(1)](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A3121+edition%3Aprelim%29); [Reg. §31.3121(d)-1(b), official CFR](https://www.govinfo.gov/content/pkg/CFR-2025-title26-vol17/pdf/CFR-2025-title26-vol17-chapI.pdf); [IRS corporate-officer guidance](https://www.irs.gov/businesses/small-businesses-self-employed/s-corporation-employees-shareholders-and-corporate-officers).

**Replacement:**

> Separate status from amount. A corporate officer is generally an employee under §3121(d)(1). The narrow exception in Reg. §31.3121(d)-1(b) applies only if the officer performs no services or only minor services and neither receives nor is entitled to remuneration. Substantial services without remuneration do not, solely by nonpayment, create a deemed wage payment; however, inspect all amounts actually or constructively paid or made available to the officer, including distributions, advances, personal expenses, and purported loans, because those amounts may be recharacterized as wages to the extent they are remuneration for services.

### 10. MEDIUM — The S-corporation section narrows AE&P to “its C years” and turns an evidence preference into a §1374 requirement

**Location:** `plugins/taxcraft/skills/tax/entities/s-corp.md:44-61`

**Exact quotes:**

> “accumulated earnings and profits from its C years”

> “Without asset-by-asset conversion-date valuations there is no NUBIG figure and no defensible §1374 number.”

**Why this is misleading:** Section 1375 tests whether the S corporation has AE&P at the close of the year; the AE&P need not arise only from that corporation’s own prior C years. IRS Form 1120-S instructions expressly note that the tax can apply after a tax-free reorganization with a C corporation. Section 1362(d)(3)’s three-consecutive-year rule and following-year effective date are correctly stated.

Section 1374 measures net unrealized built-in gain as of the first day of the first S year under its statutory aggregate formula. Asset-by-asset data is often the best way to support later recognized built-in gain/loss and is prudent workpaper practice, but the Code does not impose a universal separate-appraisal-per-asset prerequisite to having any NUBIG figure. A defensible whole-business valuation with supportable allocation may be appropriate depending on the facts.

**Primary sources:** [IRC §1375](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A1375+edition%3Aprelim%29); [IRC §1362(d)(3)](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A1362+edition%3Aprelim%29); [IRC §1374](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A1374+edition%3Aprelim%29); [Form 1120-S Instructions](https://www.irs.gov/instructions/i1120s).

**Replacement:**

> Section 1375 can apply only if the S corporation has accumulated earnings and profits at the close of the year and passive investment income exceeds 25% of gross receipts. Determine AE&P from all relevant sources, including prior C-corporation years and AE&P succeeded to in a qualifying reorganization. Section 1362(d)(3) terminates the election only after both conditions exist for three consecutive S years, effective the first day of the following tax year. For §1374, determine and support NUBIG as of the first day of the first S year under the statutory formula; obtain valuation and allocation evidence sufficient to support both aggregate NUBIG and asset-level recognition-period tracking, without stating that a separate appraisal of every asset is invariably required by the Code.

### 11. MEDIUM — The §1244 conclusion contradicts the numerical exception it just states

**Location:** `plugins/taxcraft/skills/tax/scenarios/section-1244.md:24`

**Exact quote:**

> “Net effect: operating startups virtually always pass; holding/investment companies fail.”

**Why this is wrong:** Section 1244(c)(2)(C) waives the gross-receipts composition test when the specified deductions exceed gross income for the testing period. A loss-making investment or holding company can therefore satisfy the statutory exception, while an operating startup can fail the receipts test if passive receipts dominate and the exception is not met. The categorical “pass/fail” summary overrides the correct numerical rule immediately before it.

**Primary sources:** [IRC §1244(c)(1)(C), (c)(2)(C)](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A1244+edition%3Aprelim%29); [Reg. §1.1244(c)-1, official CFR](https://www.govinfo.gov/content/pkg/CFR-2018-title26-vol13/pdf/CFR-2018-title26-vol13-part1-subjectgroup-id151.pdf); [IRS Publication 550](https://www.irs.gov/publications/p550).

**Replacement:**

> Apply the receipts test and the §1244(c)(2)(C) deductions-over-gross-income exception numerically for the statutory testing period. Business labels do not decide the result: an operating company can fail, and a holding or investment company can qualify for the exception. Report the gross-receipts fractions, the specified deductions, gross income, and the resulting statutory branch.

### 12. MEDIUM — Attorney-payment authority is misallocated, and the sourcing rule omits statutory exceptions and mixed-service allocation

**Location:** `plugins/taxcraft/skills/tax/scenarios/information-returns.md:63-67,78-88`

**Exact quotes:**

> “attorneys’ fees and gross proceeds paid to attorneys (§6045(f))”

> “Compensation for labor or personal services is sourced where the services are performed...”

**Why this is incomplete:** Corporate attorney **fees for services** are reportable under §6041/§6041A and the corporate-payee exception in Reg. §1.6041-3(p) expressly does not apply to attorneys’ fees. Section 6045(f) is the separate gross-proceeds-to-attorneys rule and excludes the portion already reportable under §6041 or §6051. Combining both under §6045(f) gives practitioners the wrong authority and can produce the wrong form/box/threshold analysis.

The place-of-performance rule is the general rule, but §861(a)(3) itself contains exceptions for certain short-term services by a nonresident alien and for certain foreign-vessel crew. Compensation for services performed partly within and partly outside the United States must be allocated under Reg. §1.861-4, generally under the method that most correctly reflects source. Residence, currency, and payment location ordinarily do not change source, but the statutory exceptions and mixed-service allocation cannot be omitted from a practitioner rule.

**Primary sources:** [Reg. §1.6041-3(p), official CFR](https://www.govinfo.gov/content/pkg/CFR-2025-title26-vol15/pdf/CFR-2025-title26-vol15-sec1-6041-3.pdf); [IRC §6045(f)](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A6045+edition%3Aprelim%29); [2026 Forms 1099-MISC/NEC Instructions](https://www.irs.gov/instructions/i1099mec); [IRC §861(a)(3)](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A861+edition%3Aprelim%29); [IRC §862(a)(3)](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A862+edition%3Aprelim%29); [Reg. §1.861-4](https://www.ecfr.gov/current/title-26/section-1.861-4).

**Replacement:**

> Corporate status generally exempts a payee under Reg. §1.6041-3(p), but the exception does not cover attorneys’ service fees or payments to corporations providing medical and health-care services. Report attorneys’ service fees under §6041/§6041A on the applicable form and box; analyze gross proceeds paid to an attorney separately under §6045(f). For services, source compensation generally by where the services are performed, subject to the express §861(a)(3) exceptions. If services are performed partly within and partly outside the United States, allocate under Reg. §1.861-4 using the method that most correctly reflects source; do not classify the entire payment by the payee’s residence, currency, or payment location.

### 13. MEDIUM — The IRIS/FIRE credential rule misstates who receives the TCC and invents an officer-or-board-action requirement

**Location:** `plugins/taxcraft/skills/tax/scenarios/information-returns.md:106-110`

**Exact quote:**

> “The Transmitter Control Code is issued against a named Responsible Official. Listing a person who holds no office and has no delegated authority is a records defect: fix it by either appointing that person to a role by board action or replacing the listing.”

**Why this is misleading:** The IRIS application is made for the firm or organization and the TCC is assigned for the organization’s selected roles and transmission methods. Responsible Officials are individuals on that application who must have responsibility for and authority over the organization; they need not hold a statutory corporate office. Authority may arise from an actual employment/delegation structure without a board appointment, depending on governing documents and entity law. FIRE and IRIS also have distinct application mechanics, so the heading should not imply that every TCC uses the same governance model.

**Primary source:** [IRS Publication 5903, IRIS Application for TCC Tutorial](https://www.irs.gov/pub/irs-pdf/p5903.pdf).

**Replacement:**

> Treat IRIS and FIRE credentials as controlled organizational records. For IRIS, the organization applies for TCCs for its selected roles and identifies the required Responsible Officials, Authorized Delegates, and contacts. Confirm that each named person in fact has the responsibility and authority required by the current IRS instructions and by the entity’s governance; a corporate office or new board appointment is not automatically required. Document the authority source and update or replace an individual who no longer qualifies. Check FIRE separately under its current application instructions.

### 14. MEDIUM — The compliance calendar gives non-universal deadlines as universal calendar-year rules

**Location:** `plugins/taxcraft/skills/tax/templates/compliance-calendar.md.template:5-12,28-39`

**Exact quotes:**

> “Calendar-year clock — information returns, payroll returns, and most state and local report, licence, and property filings, whatever the entity’s year end.”

> “Payee statements (1099 series) | January 31”

**Why this is wrong:** State annual reports and licenses can be due on an anniversary date, in a jurisdiction-assigned month, or under another cycle; they are not universally calendar-year obligations. Federal recipient-statement dates also vary by form. The 2026 General Instructions give February 15 for Forms 1099-B, 1099-DA, 1099-S, and Forms 1099-MISC reporting boxes 8 or 10, and other special dates exist. A generic template may use a lookup instruction, but it should not preload “1099 series = January 31.”

**Primary source:** [2026 IRS General Instructions for Certain Information Returns](https://www.irs.gov/publications/p1099).

**Replacement:**

> **Non-income-tax filing clock** — information returns and payroll filings generally use calendar-year or quarterly periods, but recipient and IRS due dates vary by form. State and local reports, licenses, and property filings may use a calendar year, anniversary date, assigned month, or another jurisdiction-specific period. Derive each obligation and date from the current form instructions and governing jurisdiction; do not use a universal January 31 date for the 1099 series.

> Replace the row with: `Payee statements (1099 series) | <CURRENT FORM-SPECIFIC INSTRUCTIONS — commonly January 31; February 15 or another date for specified forms/boxes> | <DATE> | | |`

### 15. MEDIUM — The retention template gives an incorrect single four-year legal floor for information returns and payee certificates

**Location:** `plugins/taxcraft/skills/tax/templates/records-retention-schedule.md.template:12-17`

**Exact quote:**

> “Information returns issued, and payee certificates | 4 years | Reg. §31.6001-1; W-9/W-8 instructions”

**Why this is wrong:** Reg. §31.6001-1 is an employment-tax record rule, not a universal four-year floor for Forms 1099 and W-8. The 2026 General Instructions generally require filed-information-return copies or reconstructable data for at least three years, with four years for Form 1099-C. Requester Form W-9 instructions use a four-year period after the last payment. W-8 requester instructions require retention for as long as the form may be relevant to liability under §§1461/1474 or the cited FATCA rule; that can be longer and is not a fixed four-year period. Basis records also remain legally relevant through the limitations period for the disposition/other return on which basis matters, not merely until that return is filed.

**Primary sources:** [2026 General Instructions for Certain Information Returns](https://www.irs.gov/publications/p1099); [Requester Instructions for Form W-9](https://www.irs.gov/instructions/iw9); [Requester Instructions for Forms W-8](https://www.irs.gov/instructions/iw8); [IRC §6001](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A6001+edition%3Aprelim%29); [Reg. §1.6001-1(e)](https://www.ecfr.gov/current/title-26/section-1.6001-1); [IRC §6501](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A6501+edition%3Aprelim%29); [Reg. §31.6001-1](https://www.ecfr.gov/current/title-26/section-31.6001-1).

**Replacement:**

> Split the row by record type: `Filed information returns and reconstructable data | Generally at least 3 years from the due date; 4 years for Form 1099-C; verify form-specific rule | Current General Instructions for Certain Information Returns`; `Forms W-9 | 4 years after the last payment | Current Requester Instructions for Form W-9`; `Forms W-8 and supporting documentation | As long as relevant to the withholding agent’s liability under §§1461/1474 and applicable regulations; apply the current form-specific validity and retention rules | Current Requester Instructions for Forms W-8`. For basis records, retain them as long as their contents may become material, ordinarily through the applicable limitations period for the return reflecting disposition or other basis use.

### 16. MEDIUM — An annual report does not prove standing, and PDF metadata is not categorical ground truth

**Location:** `plugins/taxcraft/skills/tax/governance.md:332-360`

**Exact quotes:**

> “Initial report / annual report | What the filer reported to the state, and standing as of that filing”

> “Execution metadata is ground truth.”

> “the metadata outranks the recital”

**Why this is wrong:** An annual report proves what was filed and, if agency-accepted, that the report was accepted; it does not by itself establish good standing. For example, Washington’s certificate-of-existence statute separately requires a state-issued certificate that addresses filing, fees, dissolution, and pending proceedings. Likewise, an e-sign completion certificate, notarial record, file-system timestamp, and PDF creation/modification metadata are evidence with different reliability. PDFs can be regenerated or their metadata altered. Federal Evidence Rule 901 treats authenticity as a foundation supported by the item, the process/system, and all circumstances; it does not make ordinary PDF metadata conclusive. A proven impossibility should override a false recital, but unvalidated metadata is not itself “ground truth.”

**Primary sources:** [Washington RCW 23.95.235](https://app.leg.wa.gov/RCW/default.aspx?cite=23.95.235); [DGCL §502(f), distinguishing annual reports from certificates of good standing](https://delcode.delaware.gov/title8/c005/); [Federal Rule of Evidence 901](https://uscode.house.gov/view.xhtml?req=%28title%3A28a+node232+article9+rule901+edition%3Aprelim%29).

**Replacement:**

> `Initial report / annual report | What the filed report states and, with agency acknowledgment, that it was accepted | Current good standing, internal appointment or election, or continuing truth of the reported facts; obtain a current status/certificate record under formation-state law.`

> **Execution evidence must be weighed, not ranked categorically.** Preserve and reconcile the signed document, trusted e-sign completion certificate, notarial record, delivery record, file provenance, and native/PDF metadata. Assess whether each source is authentic and reliable. If authenticated evidence proves that a recital is impossible, report the conflict and do not repeat the recital as fact; do not treat editable PDF metadata alone as conclusive.

### 17. MEDIUM — A two-party agreement does not invariably require bilateral termination or a mutual release

**Locations:** `plugins/taxcraft/skills/tax/governance.md:445-452`; `plugins/taxcraft/skills/tax/scenarios/ccorp-tax-reduction.md:198-200`; `plugins/taxcraft/skills/tax/templates/bilateral-termination-and-release.md.template:13-14,27-43`

**Exact quotes:**

> “Bilateral instruments need bilateral termination.”

> “A board resolution cannot terminate a two-party instrument.”

> “Retire it with a present-dated bilateral termination and mutual release...”

**Why this is wrong:** A board resolution cannot rewrite the counterparty’s rights, but a contract may grant the corporation a unilateral termination right; an indefinite agreement may be terminable on notice under applicable law; an agreed event can terminate it; or rescission/avoidance rules may apply. A board can authorize the corporation to exercise its own contractual termination right. Bilateral consent is necessary only when the agreement or governing law requires it. A mutual release is a separate bargain, not a universal termination element, and a blanket release can inadvertently waive fraud, indemnity, confidentiality, security, accrued-payment, tax, or other claims.

**Primary source illustrating the non-universal rule:** [UCC §2-309 as enacted in Washington, RCW 62A.2-309(2)-(3)](https://lawfilesext.leg.wa.gov/law/RCWPDF/RCW%20%2062A%20TITLE/RCW%20%2062A.%20%202%20%20CHAPTER/RCW%20%2062A.%20%202%20-309.pdf).

**Replacement:**

> Determine the instrument’s termination clause, governing law, accrued obligations, security/guaranties, and survival terms before selecting a termination route. A board action may authorize the entity to exercise a unilateral termination right but cannot, by itself, release or amend the counterparty’s rights. Use bilateral termination only when required or desired. Add a mutual release only after counsel identifies the claims and carve-outs; preserve accrued payment, fraud, indemnity, confidentiality, security, tax, and other surviving rights as applicable.

## Focused answers to the requested claims

1. **PHC before AET:** Correct. Section 532(b)(1) excludes a corporation that is a PHC under §542 from AET, so the PHC test belongs first. Correct the summary’s `> 60%` to `at least 60%`. The §533(a) preponderance statement is correct. The §547 description needs separate 90-day distribution and 120-day Form 976 deadlines. The §565 description needs consent-stock, return-filing, deemed distribution/recontribution, and shareholder-tax mechanics.
2. **June-30 C corporation:** The substantive sunset is correct for tax years beginning before January 1, 2026; the general fourth-month and six-month rules apply for tax years beginning in 2026. But current §6072(b) is the wrong citation; use §6072(a) plus Pub. L. 114-41 §2006. October 15 is one month after September 15.
3. **Related-party loans:** Section 7872 is the operative below-market-loan rule, but it expressly imports AFRs from §1274(d). Section 1274 generally governs certain debt issued for property; subsection (d) defines AFRs. The demand-loan annual and term-loan inception distinction is substantially correct with the mechanics and modification qualification stated in Finding 8. Replace the unsupported “most owner loans” assertion with the actual §7872(c)(3) test.
4. **No constructive wage from nonpayment alone:** Substantially correct as to wage amount, but it must not imply that an officer performing substantial services ceases to be an employee. Employee status and remuneration are separate inquiries; inspect constructive or relabeled payments.
5. **S corporation:** The §1375 two-condition rule and §1362(d)(3) three-year/following-year rule are correct. Replace “from its C years” with all AE&P at year-end, including succeeded-to AE&P. Section 1374 fixes the measurement date, but does not categorically command a separate appraisal of every asset.
6. **Information returns:** The PL 119-21 §70433 threshold/effective-date/indexing description is correct. Form 8233 versus W-8BEN is correct for the stated NRA personal-services treaty claim. The calendar-year reporting concept, T.D. 9972 aggregate-ten rule, and separate §§6721/6722 penalties are correct. Correct the attorney authorities, sourcing exceptions/allocation, IRIS-TCC governance description, and template deadlines.
7. **Section 1244:** The numerical §1244(c)(2)(C) exception is stated correctly; the “operating startups pass, investment companies fail” conclusion is not.
8. **Accountable-plan timing:** The 30/60/120 fixed-date safe harbors and quarterly-statement safe harbor are correct. The federal rule does not require a signed written plan, and an “annual cycle” should be analyzed item by item rather than declared wholly outside every safe harbor.
9. **Stock adequacy:** Jurisdiction-specific determination is required, but a separate signed instrument is not a universal requirement. Both MBCA and Delaware authority contradict that claim; deferred forms of consideration can also be lawful.
10. **Governance:** The authority-chain and no-false-recital principles are good controls, and the statutory/common-law/fresh-chain branching is appropriately cautious. Correct the interested-transaction safe-harbor rule, status/metadata claims, automatic §6664/criminal consequences, and universal bilateral-termination rule.
11. **Privacy and jurisdiction:** No taxpayer-specific information was found. Synthetic Washington/Delaware fixture facts are not PII. The Washington capacity citation in the generic production template is a real jurisdiction leak and the validator does not bind it to the issuer’s state.
12. **New templates:** The open-items, address/agent, incumbency, and tax-position-register templates are generally cautious. The stock-audit/closing, adequacy, related-party, bilateral-termination, compliance-calendar, and retention templates contain the material defects described above.

## Citation verification table

`VERIFIED` means the cited primary authority exists and supports the commit’s material proposition after the qualifications noted. `CORRECTED` means the commit cites the wrong provision, overstates the authority, or omits a qualification necessary for legal accuracy.

| Citation checked | Status | Primary source and result |
|---|---|---|
| IRC §§531, 532(b)(1) | VERIFIED | [U.S. Code §§531-532](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A532+edition%3Aprelim%29). AET does not apply to a PHC as defined in §542. |
| IRC §533(a) | VERIFIED | [U.S. Code §533](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A533+edition%3Aprelim%29). Accumulation beyond reasonable needs is determinative unless rebutted by a preponderance. |
| IRC §§541-545 | CORRECTED | [§542](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A542+edition%3Aprelim%29). Income test is at least 60%, not greater than 60%; ownership/attribution ordering otherwise supported. |
| Reg. §1.537-2(c) | VERIFIED | [eCFR §1.537-2](https://www.ecfr.gov/current/title-26/section-1.537-2). Loans to shareholders can evidence accumulations beyond reasonable business needs. |
| IRC §547; Form 976 | CORRECTED | [U.S. Code §547](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A547+edition%3Aprelim%29); [IRS Form 976](https://www.irs.gov/forms-pubs/about-form-976). Distribution within 90 days and before claim; claim within 120 days; no relief for related interest/additional amounts/assessable penalties. |
| IRC §565 | CORRECTED | [U.S. Code §565](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A565+edition%3Aprelim%29). Requires last-day consent stock, consent filed with return, and deemed distribution/recontribution. |
| IRC §6072(a), (b) | CORRECTED | [current U.S. Code §6072](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A6072+edition%3Aprelim%29). Current subsection (a) has general fourth-month rule; subsection (b) is partnership/S-corporation rule. |
| Pub. L. 114-41 §2006 | VERIFIED | [official public law](https://www.govinfo.gov/content/pkg/PLAW-114publ41/pdf/PLAW-114publ41.pdf). June-30 C-corporation transition applies to tax years beginning after December 31, 2025, so prior rule remains for years beginning before 2026. |
| Form 7004 extension rule | VERIFIED | [IRS Instructions](https://www.irs.gov/instructions/i7004). Seven months for June-30 C-corporation years beginning before 2026; six months for years beginning in 2026. |
| IRC §7872 | CORRECTED | [U.S. Code §7872](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A7872+edition%3Aprelim%29). Demand/term mechanics generally support the distinction; §7872 imports §1274(d) AFRs and §7872(c)(3) supplies a $10,000 conditional exception. |
| IRC §1274(d) | CORRECTED | [U.S. Code §1274](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A1274+edition%3Aprelim%29). Section 1274 governs certain property-sale debt; subsection (d) determines AFRs also used by §7872. |
| IRC §3121(d)(1); Reg. §31.3121(d)-1(b) | CORRECTED | [U.S. Code §3121](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A3121+edition%3Aprelim%29); [official CFR](https://www.govinfo.gov/content/pkg/CFR-2025-title26-vol17/pdf/CFR-2025-title26-vol17-chapI.pdf). Officer is generally an employee; exception requires minor/no services and no receipt or entitlement. No remuneration paid means no wage solely from nonpayment. |
| IRC §1375 | CORRECTED | [U.S. Code §1375](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A1375+edition%3Aprelim%29). Tests AE&P at year-end, not only E&P from that corporation’s own C years. |
| IRC §1362(d)(3) | VERIFIED | [U.S. Code §1362](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A1362+edition%3Aprelim%29). Both conditions for three consecutive S years; termination first day of following year. |
| IRC §1374 | CORRECTED | [U.S. Code §1374](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A1374+edition%3Aprelim%29). Conversion-date measurement is correct; universal asset-by-asset appraisal requirement is not in the statute. |
| IRC §1244(c) and Reg. §1.1244(c)-1 | CORRECTED | [U.S. Code §1244](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A1244+edition%3Aprelim%29); [official CFR](https://www.govinfo.gov/content/pkg/CFR-2018-title26-vol13/pdf/CFR-2018-title26-vol13-part1-subjectgroup-id151.pdf). Numerical tests are correct; categorical business-type conclusion is not. |
| IRC §62(c); Reg. §1.62-2 | CORRECTED | [U.S. Code §62](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A62+edition%3Aprelim%29); [eCFR](https://www.ecfr.gov/current/title-26/section-1.62-2). Three substantive requirements and safe harbors verified; no signed-writing prerequisite. |
| Rev. Rul. 2012-25 | VERIFIED | [IRS IRB 2012-37](https://www.irs.gov/irb/2012-37_IRB). Wage recharacterization rule supported; it does not add a written-plan requirement. |
| IRC §274(d), §280A(c)(1), §121 | VERIFIED | [§274](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A274+edition%3Aprelim%29); [§280A](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A280A+edition%3Aprelim%29); [§121](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A121+edition%3Aprelim%29). Cross-reference descriptions in the router are accurate at the level stated. |
| PL 119-21 §70433; IRC §§6041(a), 6041A(a)(2), 6041(h) | VERIFIED | [official Pub. L. 119-21](https://www.govinfo.gov/content/pkg/PLAW-119publ21/pdf/PLAW-119publ21.pdf); [current §6041](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A6041+edition%3Aprelim%29); [current §6041A](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A6041A+edition%3Aprelim%29). $2,000 threshold applies to payments after 2025; indexing begins after 2026. |
| PL 119-21 §70432; IRC §6050W | VERIFIED | [official Pub. L. 119-21](https://www.govinfo.gov/content/pkg/PLAW-119publ21/pdf/PLAW-119publ21.pdf); [U.S. Code §6050W](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A6050W+edition%3Aprelim%29). Restoration described at the level stated. |
| Reg. §1.6041-3(p); IRC §6045(f) | CORRECTED | [official CFR](https://www.govinfo.gov/content/pkg/CFR-2025-title26-vol15/pdf/CFR-2025-title26-vol15-sec1-6041-3.pdf); [U.S. Code §6045](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A6045+edition%3Aprelim%29). Corporate exceptions verified; service fees and gross proceeds require separate authority analysis. |
| IRC §3406 | VERIFIED | [U.S. Code §3406](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A3406+edition%3Aprelim%29). Backup withholding applies to covered reportable payments on statutory triggers; current operational timing remains form/notice-specific. |
| IRC §§861(a)(3), 862(a)(3); Reg. §1.861-4 | CORRECTED | [§861](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A861+edition%3Aprelim%29); [§862](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A862+edition%3Aprelim%29); [eCFR §1.861-4](https://www.ecfr.gov/current/title-26/section-1.861-4). General place-of-performance rule verified; statutory exceptions and mixed-service allocation omitted. |
| IRC §§1441, 1461; Reg. §1.6302-2 | VERIFIED | [§1441](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A1441+edition%3Aprelim%29); [§1461](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A1461+edition%3Aprelim%29); [eCFR §1.6302-2](https://www.ecfr.gov/current/title-26/section-1.6302-2). Withholding-agent liability and deposit framework support the stated warning, subject to classification/treaty/documentation rules. |
| T.D. 9972 | VERIFIED | [official Federal Register rule](https://www.federalregister.gov/documents/2023/02/23/2023-03710/electronic-filing-requirements-for-specified-returns-and-other-documents). Aggregate-ten electronic-filing rule effective for returns required on or after January 1, 2024. |
| IRC §§6721, 6722 | VERIFIED | [§6721](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A6721+edition%3Aprelim%29); [§6722](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A6722+edition%3Aprelim%29). Separate filing and payee-statement penalties; intentional-disregard tiers have no maximum. |
| IRC §§6001, 6501; Reg. §1.6001-1 | CORRECTED | [§6001](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A6001+edition%3Aprelim%29); [§6501](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A6501+edition%3Aprelim%29); [eCFR §1.6001-1](https://www.ecfr.gov/current/title-26/section-1.6001-1). Materiality/limitations principle supported; basis-record phrasing is too short. |
| Reg. §31.6001-1 | CORRECTED | [eCFR §31.6001-1](https://www.ecfr.gov/current/title-26/section-31.6001-1). Supports four-year employment-tax records, not a universal four-year W-8/1099 rule. |
| IRC §6664(c); Reg. §1.6664-4 | CORRECTED | [§6664](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A6664+edition%3Aprelim%29); [eCFR §1.6664-4](https://www.ecfr.gov/current/title-26/section-1.6664-4). Relief is portion-specific and fact-specific; no automatic file-wide forfeiture. |
| IRC §7206; 18 U.S.C. §1001 | CORRECTED | [IRC §7206](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A7206+edition%3Aprelim%29); [18 U.S.C. §1001](https://uscode.house.gov/view.xhtml?req=%28title%3A18+section%3A1001+edition%3Aprelim%29). Potential exposure is real only when each offense’s elements are met. |
| IRC §§83, 351, 358, 362, 368(c); Regs. §§1.351-1, 1.351-3, 1.358-2 | VERIFIED | [§83](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A83+edition%3Aprelim%29); [§351](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A351+edition%3Aprelim%29); [§358](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A358+edition%3Aprelim%29); [§362](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A362+edition%3Aprelim%29); [§368](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A368+edition%3Aprelim%29); [Reg. §1.351-1](https://www.ecfr.gov/current/title-26/section-1.351-1); [Reg. §1.351-3](https://www.ecfr.gov/current/title-26/section-1.351-3); [Reg. §1.358-2](https://www.ecfr.gov/current/title-26/section-1.358-2). Source mappings are real; template conclusions cannot be pre-verified from citation presence alone. |
| IRC §§1202, 1244, 248 | VERIFIED | [§1202](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A1202+edition%3Aprelim%29); [§1244](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A1244+edition%3Aprelim%29); [§248](https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A248+edition%3Aprelim%29). Cross-reference subjects are correct; §1244 issue described in Finding 11 and no qualification can be presumed in a blank template. |
| MBCA §6.21 | CORRECTED | [ABA official MBCA resource](https://www.americanbar.org/groups/business_law/resources/model-business-corporation-act/). Official comment expressly permits adequacy to be inferred from an issuance authorization and permits notes/future services subject to statutory protections. |
| DGCL §§152, 156 | CORRECTED | [Delaware Code](https://delcode.delaware.gov/title8/c001/sc05/). Issuance terms may be in the board resolution; partly paid shares are permitted. |
| DGCL §144; MBCA §§8.61-8.63 | CORRECTED | [Delaware Code §144](https://delcode.delaware.gov/title8/c001/sc04/); [ABA MBCA resource](https://www.americanbar.org/groups/business_law/resources/model-business-corporation-act/). Disinterested-stockholder/qualified-share alternatives defeat “fairness only.” |
| DGCL §§204-205 / MBCA defective-action framework | VERIFIED | [Delaware Code §§204-205](https://delcode.delaware.gov/title8/c001/sc06/); [ABA MBCA resource](https://www.americanbar.org/groups/business_law/resources/model-business-corporation-act/). The commit’s three-branch, counsel-routed treatment is appropriately cautious; availability remains jurisdiction- and act-specific. |
| RCW 23B.06.310 | CORRECTED | [Washington Legislature](https://app.leg.wa.gov/RCW/default.aspx?cite=23B.06.310). It is a valid Washington source but cannot be the default capacity authority for a state-neutral template. |

## Independent-review and verification notes

- I ran the project-required Claude review gate twice using the authenticated repo-root wrapper and the default Opus reviewer. Both runs ended with `REVIEW FAILED: envelope error: subtype=success api_error=None term=api_error`. No Claude result or signoff was available, and the failures were not treated as approval.
- The review was legal/doctrinal and commit-pinned. I did not alter source files, run a moving-HEAD legal comparison, or rely on later remediation commits.
- No taxpayer-specific information was found in the commit’s added taxcraft content.

VERDICT: NOT APPROVED
