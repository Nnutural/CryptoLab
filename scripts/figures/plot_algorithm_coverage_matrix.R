#!/usr/bin/env Rscript

local_lib <- "D:/Development/R/library/4.6"
if (dir.exists(local_lib) && !(local_lib %in% .libPaths())) {
  .libPaths(c(local_lib, .libPaths()))
}

suppressPackageStartupMessages({
  library(ggplot2)
  library(patchwork)
  library(readr)
  library(dplyr)
  library(tidyr)
  library(scales)
  library(svglite)
  library(ragg)
})

script_file <- normalizePath(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1]), winslash = "/", mustWork = TRUE)
root <- normalizePath(file.path(dirname(script_file), "..", ".."), winslash = "/", mustWork = TRUE)
data_dir <- file.path(root, "docs", "report_assets", "data")
fig_dir <- file.path(root, "docs", "report_assets", "figures")
dir.create(data_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(fig_dir, recursive = TRUE, showWarnings = FALSE)

theme_nature_contract <- function(base_size = 6.8, base_family = "Arial") {
  theme_classic(base_size = base_size, base_family = base_family) +
    theme(
      axis.line = element_blank(),
      axis.ticks = element_blank(),
      axis.title = element_text(size = base_size),
      axis.text = element_text(size = base_size - 0.3, colour = "#222222"),
      legend.title = element_text(size = base_size - 0.3),
      legend.text = element_text(size = base_size - 0.7),
      strip.text = element_text(size = base_size - 0.2, face = "bold"),
      plot.title = element_text(size = base_size + 0.7, face = "bold"),
      panel.grid = element_blank()
    )
}

save_pub_r <- function(plot, filename, width_mm = 183, height_mm = 115, dpi = 320) {
  w <- width_mm / 25.4
  h <- height_mm / 25.4
  svglite::svglite(paste0(filename, ".svg"), width = w, height = h)
  print(plot)
  dev.off()
  ragg::agg_png(paste0(filename, ".png"), width = w, height = h, units = "in", res = dpi, background = "white")
  print(plot)
  dev.off()
}

theme_set(theme_nature_contract())

coverage <- tibble::tribble(
  ~category, ~algorithm, ~status, ~status_label, ~vector_source, ~library_reference, ~source_evidence, ~risk_note, ~column_order,
  "Encoding", "Base64", "implemented_tested", "Full", "RFC 4648", "Python base64", "docs/PROGRESS.md; docs/cross_validation_matrix.md; rust_core/src/encoding/base64.rs", "None", 1,
  "Encoding", "UTF-8", "implemented_tested", "Full", "RFC 3629 / Unicode", "Python codec", "docs/PROGRESS.md; docs/cross_validation_matrix.md; rust_core/src/encoding/utf8.rs", "None", 2,
  "Hash", "SHA1", "implemented_tested", "Full", "FIPS 180-4 / RFC", "hashlib", "docs/PROGRESS.md; docs/cross_validation_matrix.md; rust_core/src/hash/sha1.rs", "None", 3,
  "Hash", "SHA256", "implemented_tested", "Full", "FIPS 180-4 / RFC", "hashlib", "docs/PROGRESS.md; docs/cross_validation_matrix.md; rust_core/src/hash/sha2.rs", "None", 4,
  "Hash", "SHA3", "implemented_tested", "Full", "NIST / RFC", "hashlib", "docs/PROGRESS.md; docs/cross_validation_matrix.md; rust_core/src/hash/sha3.rs", "None", 5,
  "Hash", "RIPEMD160", "implemented_tested", "Full", "RFC/NIST matrix", "hashlib", "docs/PROGRESS.md; docs/cross_validation_matrix.md; rust_core/src/hash/ripemd.rs", "None", 6,
  "Hash", "HMAC-SHA1", "implemented_tested", "Full", "RFC 2202", "stdlib hmac", "docs/PROGRESS.md; docs/cross_validation_matrix.md; rust_core/src/hash/hmac.rs", "None", 7,
  "Hash", "HMAC-SHA256", "implemented_tested", "Full", "RFC 4231", "stdlib hmac", "docs/PROGRESS.md; docs/cross_validation_matrix.md; rust_core/src/hash/hmac.rs", "None", 8,
  "Hash", "PBKDF2", "implemented_tested", "Full", "RFC vectors", "cryptography", "docs/PROGRESS.md; docs/cross_validation_matrix.md; rust_core/src/hash/pbkdf2.rs", "None", 9,
  "Symmetric", "AES", "implemented_tested", "Full", "NIST SP 800-38A/38D; FIPS 197", "cryptography", "docs/PROGRESS.md; docs/cross_validation_matrix.md; rust_core/src/symmetric/aes.rs", "None", 10,
  "Symmetric", "SM4", "implemented_tested", "Full", "GB/T 32907", "gmssl", "docs/PROGRESS.md; docs/cross_validation_matrix.md; rust_core/src/symmetric/sm4.rs", "None", 11,
  "Symmetric", "RC6", "partial", "Partial", "RC6 paper vectors", "N/A", "docs/PROGRESS.md; docs/cross_validation_matrix.md; rust_core/src/symmetric/rc6.rs", "Mode coverage limited to ECB/CBC; KAT-only library comparison", 12,
  "Public key", "RSA-1024", "implemented_tested", "Full", "RFC 8017", "cryptography", "docs/PROGRESS.md; docs/cross_validation_matrix.md; rust_core/src/pubkey/rsa.rs", "Slow RSA stress tests ignored by design", 13,
  "Public key", "ECC-160", "implemented_tested", "Full", "secp160r1", "internal KAT", "docs/PROGRESS.md; rust_core/src/pubkey/ecc.rs", "Mainstream cryptography package lacks secp160r1", 14,
  "Public key", "ECDSA", "implemented_tested", "Full", "RFC 6979", "KAT-only", "docs/PROGRESS.md; docs/cross_validation_matrix.md; rust_core/src/pubkey/ecdsa.rs", "secp160r1 third-party reference unavailable", 15
)

write_csv(coverage, file.path(data_dir, "fig2_algorithm_coverage_matrix.csv"))

coverage <- coverage %>%
  mutate(
    category = factor(category, levels = c("Encoding", "Hash", "Symmetric", "Public key")),
    algorithm = factor(algorithm, levels = coverage$algorithm),
    status_label = factor(status_label, levels = c("Full", "Partial", "Missing"))
  )

status_cols <- c(Full = "#2F5D8C", Partial = "#D6A64A", Missing = "#B85C5C")

p_matrix <- ggplot(coverage, aes(x = algorithm, y = category, fill = status_label)) +
  geom_tile(colour = "white", linewidth = 0.6, height = 0.78) +
  geom_text(aes(label = status_label), size = 2.05, colour = "white", fontface = "bold") +
  scale_fill_manual(values = status_cols, drop = FALSE, name = "Implementation status") +
  scale_x_discrete(position = "top") +
  labs(
    title = "Course algorithm coverage",
    x = NULL,
    y = NULL
  ) +
  theme(
    axis.text.x = element_text(angle = 42, hjust = 0, vjust = 0.5),
    legend.position = "bottom",
    plot.margin = margin(5.5, 5.5, 0, 5.5)
  )

source_long <- coverage %>%
  select(algorithm, vector_source, library_reference) %>%
  pivot_longer(c(vector_source, library_reference), names_to = "evidence_type", values_to = "evidence") %>%
  mutate(
    evidence_type = recode(evidence_type, vector_source = "KAT / standard", library_reference = "Reference library"),
    evidence_type = factor(evidence_type, levels = c("KAT / standard", "Reference library")),
    evidence_short = case_when(
      grepl("N/A|KAT-only|internal", evidence) ~ "Limited",
      TRUE ~ "External"
    )
  )

p_sources <- ggplot(source_long, aes(x = algorithm, y = evidence_type, fill = evidence_short)) +
  geom_tile(colour = "white", linewidth = 0.55, height = 0.72) +
  geom_text(aes(label = evidence), size = 1.62, lineheight = 0.86, colour = "#222222") +
  scale_fill_manual(values = c(External = "#DDEAF6", Limited = "#F1E0B7"), name = "Evidence type") +
  scale_x_discrete(position = "top") +
  labs(
    title = "Test-vector and reference evidence",
    x = NULL,
    y = NULL
  ) +
  theme(
    axis.text.x = element_blank(),
    legend.position = "none",
    plot.margin = margin(0, 5.5, 5.5, 5.5)
  )

fig <- (p_matrix / p_sources) +
  plot_layout(heights = c(1.05, 1.15), guides = "collect") +
  plot_annotation(
    title = "Algorithm implementation coverage is complete, with RC6 mode limits disclosed",
    tag_levels = "a"
  ) &
  theme(
    plot.tag = element_text(size = 8.5, face = "bold"),
    plot.title = element_text(size = 8.2, face = "bold"),
    legend.position = "bottom"
  )

save_pub_r(fig, file.path(fig_dir, "fig2_algorithm_coverage_matrix"))
