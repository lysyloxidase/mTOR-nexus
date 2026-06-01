# Restricted source staging

Raw PhosphoSitePlus and COSMIC exports are licensed resources and must never be
committed to the open atlas repository. Place licensed local snapshots in this
directory only while rebuilding derived exports. The directory is ignored
except for this policy note and its non-sensitive manifests.

Committed graph edges may retain a PhosphoSitePlus site identifier so curators
can reconcile a claim against their licensed local copy.

Local COSMIC reconciliation expects a curator-provided TSV with the columns
`COSMIC_ID`, `GENE_SYMBOL`, and `HGVSP`. Open artifacts retain the segregation
boundary, not restricted mutation rows.
