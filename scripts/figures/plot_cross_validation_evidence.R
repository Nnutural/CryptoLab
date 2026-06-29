#!/usr/bin/env Rscript

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

root <- normalizePath(file.path(dirname(sys.frame(1)$ofile), "..", ".."), winslash = "/", mustWork = TRUE)
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
      axis.text = element_text(size = base_size - 0.25, colour = "#222222"),
      legend.title = element_text(size = base_size - 0.3),
      legend.text = element_text(size = base_size - 0.7),
      strip.text = element_text(size = base_size - 0.2, face = "bold"),
      plot.title = element_text(size = base_size + 0.7, face = "bold"),
      panel.grid = element_blank()
    )
}

save_pub_r <- function(plot, filename, width_mm = 183, height_mm = 125, dpi = 320) {
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

evidence <- tibble::tribble(
  ~algorithm, ~evidence_layer, ~status, ~status_label, ~source_evidence, ~note,
  "AES", "KAT standard vectors", "pass", "Pass", "docs/cross_validation_matrix.md; api_server/tests/test_cross_validation.py", "NIST/FIPS vectors",
  "AES", "Third-party reference", "pass", "Pass", "docs/cross_validation_matrix.md", "cryptography",
  "AES", "HTTP API tests", "pass", "Pass", "api_server/tests/test_cross_validation.py; api_server/tests/test_aes_verbose.py", "encrypt endpoint cross-validation",
  "AES", "Frontend build/integration", "partial", "Partial", "docs/PROGRESS.md; docs/progress_evidence/23_frontend_build_tail.txt", "build passes; npm test historical status differs",
  "AES", "Verbose/demo support", "pass", "Pass", "docs/aes_verbose_trace_fips197.json; api_server/tests/test_aes_verbose.py", "FIPS trace",
  "SM4", "KAT standard vectors", "pass", "Pass", "docs/cross_validation_matrix.md", "GB/T vectors",
  "SM4", "Third-party reference", "pass", "Pass", "docs/cross_validation_matrix.md", "gmssl",
  "SM4", "HTTP API tests", "pass", "Pass", "api_server/tests/test_cross_validation.py", "ECB/CBC API validation",
  "SM4", "Frontend build/integration", "partial", "Partial", "docs/PROGRESS.md", "view and build evidence",
  "SM4", "Verbose/demo support", "none", "No evidence", "docs/verbose_mode.md", "verbose mode is AES-only",
  "RC6", "KAT standard vectors", "pass", "Pass", "docs/cross_validation_matrix.md", "Rivest/Krovetz vectors",
  "RC6", "Third-party reference", "none", "No evidence", "docs/cross_validation_matrix.md", "mainstream Python crypto libraries do not ship RC6",
  "RC6", "HTTP API tests", "pass", "Pass", "api_server/tests/test_cross_validation.py", "KAT-only API path",
  "RC6", "Frontend build/integration", "partial", "Partial", "docs/PROGRESS.md", "view and build evidence",
  "RC6", "Verbose/demo support", "none", "No evidence", "docs/verbose_mode.md", "not a verbose/demo target",
  "SHA family", "KAT standard vectors", "pass", "Pass", "docs/cross_validation_matrix.md", "RFC/NIST",
  "SHA family", "Third-party reference", "pass", "Pass", "docs/cross_validation_matrix.md", "hashlib",
  "SHA family", "HTTP API tests", "pass", "Pass", "api_server/tests/test_cross_validation.py", "hash endpoints",
  "SHA family", "Frontend build/integration", "partial", "Partial", "docs/PROGRESS.md", "hash view build evidence",
  "SHA family", "Verbose/demo support", "none", "No evidence", "docs/verbose_mode.md", "not a verbose/demo target",
  "HMAC", "KAT standard vectors", "pass", "Pass", "docs/cross_validation_matrix.md", "RFC vectors",
  "HMAC", "Third-party reference", "pass", "Pass", "docs/cross_validation_matrix.md", "stdlib hmac",
  "HMAC", "HTTP API tests", "pass", "Pass", "api_server/tests/test_cross_validation.py", "hmac endpoint",
  "HMAC", "Frontend build/integration", "partial", "Partial", "docs/PROGRESS.md", "HmacPbkdf2View build evidence",
  "HMAC", "Verbose/demo support", "none", "No evidence", "docs/verbose_mode.md", "not a verbose/demo target",
  "PBKDF2", "KAT standard vectors", "pass", "Pass", "docs/cross_validation_matrix.md", "RFC-style vectors",
  "PBKDF2", "Third-party reference", "pass", "Pass", "docs/cross_validation_matrix.md", "cryptography",
  "PBKDF2", "HTTP API tests", "pass", "Pass", "api_server/tests/test_cross_validation.py; api_server/tests/test_benchmark.py", "pbkdf2 endpoint and benchmark",
  "PBKDF2", "Frontend build/integration", "partial", "Partial", "docs/PROGRESS.md", "HmacPbkdf2View and DemosView build evidence",
  "PBKDF2", "Verbose/demo support", "pass", "Pass", "api_server/app/services/demos_service.py", "iteration-impact demo",
  "RSA", "KAT standard vectors", "pass", "Pass", "docs/cross_validation_matrix.md", "RFC 8017",
  "RSA", "Third-party reference", "pass", "Pass", "docs/cross_validation_matrix.md", "cryptography",
  "RSA", "HTTP API tests", "pass", "Pass", "api_server/tests/test_cross_validation.py; api_server/tests/test_benchmark.py", "OAEP/PSS endpoints",
  "RSA", "Frontend build/integration", "partial", "Partial", "docs/PROGRESS.md", "RsaView build evidence",
  "RSA", "Verbose/demo support", "pass", "Pass", "api_server/app/services/demos_service.py", "low-exponent demo",
  "ECDSA", "KAT standard vectors", "pass", "Pass", "docs/cross_validation_matrix.md", "RFC 6979",
  "ECDSA", "Third-party reference", "none", "No evidence", "docs/cross_validation_matrix.md", "cryptography lacks secp160r1",
  "ECDSA", "HTTP API tests", "pass", "Pass", "api_server/tests/test_cross_validation.py; api_server/tests/test_benchmark.py", "sign/verify endpoints",
  "ECDSA", "Frontend build/integration", "partial", "Partial", "docs/PROGRESS.md", "EccView build evidence",
  "ECDSA", "Verbose/demo support", "pass", "Pass", "api_server/app/services/demos_service.py", "k-reuse demo",
  "Base64", "KAT standard vectors", "pass", "Pass", "docs/cross_validation_matrix.md", "RFC 4648",
  "Base64", "Third-party reference", "pass", "Pass", "docs/cross_validation_matrix.md", "Python base64",
  "Base64", "HTTP API tests", "pass", "Pass", "api_server/tests/test_cross_validation.py", "encoding endpoint",
  "Base64", "Frontend build/integration", "partial", "Partial", "docs/PROGRESS.md", "EncodingView build evidence",
  "Base64", "Verbose/demo support", "none", "No evidence", "docs/verbose_mode.md", "not a verbose/demo target",
  "UTF-8", "KAT standard vectors", "pass", "Pass", "docs/cross_validation_matrix.md", "Unicode",
  "UTF-8", "Third-party reference", "pass", "Pass", "docs/cross_validation_matrix.md", "Python codec",
  "UTF-8", "HTTP API tests", "pass", "Pass", "api_server/tests/test_cross_validation.py", "encoding endpoint plus rejection case",
  "UTF-8", "Frontend build/integration", "partial", "Partial", "docs/PROGRESS.md", "EncodingView build evidence",
  "UTF-8", "Verbose/demo support", "none", "No evidence", "docs/verbose_mode.md", "not a verbose/demo target"
)

write_csv(evidence, file.path(data_dir, "fig3_cross_validation_evidence.csv"))

algorithm_levels <- c("AES", "SM4", "RC6", "SHA family", "HMAC", "PBKDF2", "RSA", "ECDSA", "Base64", "UTF-8")
layer_levels <- c("KAT standard vectors", "Third-party reference", "HTTP API tests", "Frontend build/integration", "Verbose/demo support")

evidence <- evidence %>%
  mutate(
    algorithm = factor(algorithm, levels = rev(algorithm_levels)),
    evidence_layer = factor(evidence_layer, levels = layer_levels),
    status_label = factor(status_label, levels = c("Pass", "Partial", "No evidence"))
  )

status_cols <- c(Pass = "#2F5D8C", Partial = "#D6A64A", `No evidence` = "#D9D9D9")
status_text <- c(Pass = "P", Partial = "Part", `No evidence` = "None")

p_matrix <- ggplot(evidence, aes(x = evidence_layer, y = algorithm, fill = status_label)) +
  geom_tile(colour = "white", linewidth = 0.55, height = 0.82) +
  geom_text(aes(label = unname(status_text[as.character(status_label)])), size = 2.05, colour = "#222222", fontface = "bold") +
  scale_fill_manual(values = status_cols, drop = FALSE, name = "Evidence status") +
  labs(
    title = "Evidence layers by algorithm family",
    x = NULL,
    y = NULL
  ) +
  theme(
    axis.text.x = element_text(angle = 30, hjust = 1, vjust = 1),
    legend.position = "bottom"
  )

summary_counts <- evidence %>%
  count(evidence_layer, status_label) %>%
  mutate(evidence_layer = factor(evidence_layer, levels = layer_levels))

p_counts <- ggplot(summary_counts, aes(x = evidence_layer, y = n, fill = status_label)) +
  geom_col(width = 0.68, colour = "white", linewidth = 0.35) +
  geom_text(aes(label = n), position = position_stack(vjust = 0.5), size = 2.1, colour = "#222222") +
  scale_fill_manual(values = status_cols, drop = FALSE, name = "Evidence status") +
  labs(
    title = "Evidence-cell counts",
    x = NULL,
    y = "cells (count)"
  ) +
  theme(
    axis.line.y = element_line(linewidth = 0.35),
    axis.text.x = element_text(angle = 30, hjust = 1, vjust = 1),
    legend.position = "none"
  )

fig <- (p_matrix / p_counts) +
  plot_layout(heights = c(1.8, 1), guides = "collect") +
  plot_annotation(
    title = "Cross-validation evidence spans standards, libraries, APIs and demos",
    tag_levels = "a"
  ) &
  theme(
    plot.tag = element_text(size = 8.5, face = "bold"),
    plot.title = element_text(size = 8.2, face = "bold"),
    legend.position = "bottom"
  )

save_pub_r(fig, file.path(fig_dir, "fig3_cross_validation_evidence"))

