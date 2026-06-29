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

args <- commandArgs(FALSE)
file_arg <- grep("^--file=", args, value = TRUE)
if (length(file_arg) > 0) {
  script_file <- normalizePath(sub("^--file=", "", file_arg[1]), winslash = "/", mustWork = TRUE)
  root <- normalizePath(file.path(dirname(script_file), "..", ".."), winslash = "/", mustWork = TRUE)
} else {
  root <- normalizePath(getwd(), winslash = "/", mustWork = TRUE)
}

data_dir <- file.path(root, "docs", "report_assets", "data")
fig_dir <- file.path(root, "docs", "report_assets", "figures")
dir.create(data_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(fig_dir, recursive = TRUE, showWarnings = FALSE)

status_cols <- c(
  "Full" = "#2E5E8C",
  "Pass" = "#2E5E8C",
  "Partial" = "#D9A441",
  "Limited" = "#E8D6A3",
  "Missing" = "#D9D9D9",
  "None" = "#D9D9D9",
  "No evidence" = "#D9D9D9",
  "External" = "#DCEAF5"
)

theme_journal <- function(base_size = 6.2, base_family = "Arial") {
  theme_classic(base_size = base_size, base_family = base_family) +
    theme(
      plot.background = element_rect(fill = "white", colour = NA),
      panel.background = element_rect(fill = "white", colour = NA),
      axis.line = element_blank(),
      axis.ticks = element_blank(),
      axis.title = element_text(size = base_size, colour = "#222222"),
      axis.text = element_text(size = base_size - 0.2, colour = "#222222"),
      plot.title = element_text(size = 7.1, face = "bold", colour = "#111111", hjust = 0),
      plot.caption = element_text(size = 4.8, colour = "#444444", hjust = 0, lineheight = 0.94),
      legend.position = "bottom",
      legend.direction = "horizontal",
      legend.title = element_blank(),
      legend.text = element_text(size = 5.6, colour = "#222222"),
      legend.key.size = unit(3.2, "mm"),
      legend.spacing.x = unit(1.2, "mm"),
      panel.grid = element_blank(),
      plot.margin = margin(2.5, 2.5, 2.5, 2.5)
    )
}

save_journal <- function(plot, filename, width_mm = 183, height_mm = 132, dpi = 450) {
  w <- width_mm / 25.4
  h <- height_mm / 25.4

  grDevices::cairo_pdf(paste0(filename, ".pdf"), width = w, height = h, family = "Arial", bg = "white")
  print(plot)
  dev.off()

  ragg::agg_png(paste0(filename, ".png"), width = w, height = h, units = "in", res = dpi, background = "white")
  print(plot)
  dev.off()
}

theme_set(theme_journal())

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

category_levels <- c("Encoding", "Hash", "Symmetric", "Public key")
algorithm_levels <- coverage$algorithm
algorithm_labels <- c(
  "Base64" = "Base64",
  "UTF-8" = "UTF-8",
  "SHA1" = "SHA1",
  "SHA256" = "SHA256",
  "SHA3" = "SHA3",
  "RIPEMD160" = "RIPEMD\n160",
  "HMAC-SHA1" = "HMAC-\nSHA1",
  "HMAC-SHA256" = "HMAC-\nSHA256",
  "PBKDF2" = "PBKDF2",
  "AES" = "AES",
  "SM4" = "SM4",
  "RC6" = "RC6",
  "RSA-1024" = "RSA-\n1024",
  "ECC-160" = "ECC-\n160",
  "ECDSA" = "ECDSA"
)

coverage_plot <- coverage %>%
  mutate(
    category = factor(category, levels = category_levels),
    algorithm = factor(algorithm, levels = algorithm_levels),
    status_label = factor(status_label, levels = c("Full", "Partial", "Missing", "External", "Limited")),
    status_symbol = case_when(
      status_label == "Full" ~ "\u2713",
      status_label == "Partial" ~ "Part.",
      TRUE ~ "\u2014"
    ),
    symbol_colour = case_when(
      status_label == "Full" ~ "white",
      TRUE ~ "#222222"
    ),
    kat_code = case_when(
      algorithm == "Base64" ~ "K1",
      algorithm == "UTF-8" ~ "K2",
      algorithm %in% c("SHA1", "SHA256") ~ "K3",
      algorithm %in% c("SHA3", "RIPEMD160") ~ "K4",
      algorithm %in% c("HMAC-SHA1", "HMAC-SHA256") ~ "K5",
      algorithm == "PBKDF2" ~ "K6",
      algorithm == "AES" ~ "K7",
      algorithm == "SM4" ~ "K8",
      algorithm == "RC6" ~ "K9",
      algorithm == "RSA-1024" ~ "K10",
      algorithm == "ECC-160" ~ "K11",
      algorithm == "ECDSA" ~ "K12",
      TRUE ~ "KAT"
    ),
    library_code = case_when(
      algorithm %in% c("Base64", "UTF-8") ~ "L1",
      algorithm %in% c("SHA1", "SHA256", "SHA3", "RIPEMD160", "HMAC-SHA1", "HMAC-SHA256") ~ "L2",
      algorithm %in% c("PBKDF2", "AES", "RSA-1024") ~ "L3",
      algorithm == "SM4" ~ "L4",
      algorithm %in% c("ECC-160", "ECDSA") ~ "L5",
      algorithm == "RC6" ~ "\u2014",
      TRUE ~ "\u2014"
    )
  )

write_csv(coverage_plot, file.path(data_dir, "fig2_algorithm_coverage_refined.csv"))

background_grid <- tidyr::expand_grid(
  category = factor(category_levels, levels = category_levels),
  algorithm = factor(algorithm_levels, levels = algorithm_levels)
)

fill_breaks_fig2 <- c("Full", "Partial", "Missing", "External", "Limited")
fill_labels_fig2 <- c("Full", "Partial", "Missing / none", "External evidence", "Limited evidence")

p_coverage <- ggplot() +
  geom_tile(
    data = background_grid,
    aes(x = algorithm, y = category),
    fill = "#F7F7F7",
    colour = "#ECECEC",
    linewidth = 0.25,
    width = 0.94,
    height = 0.82
  ) +
  geom_tile(
    data = coverage_plot,
    aes(x = algorithm, y = category, fill = status_label),
    colour = "white",
    linewidth = 0.28,
    width = 0.94,
    height = 0.82
  ) +
  geom_text(
    data = coverage_plot,
    aes(x = algorithm, y = category, label = status_symbol, colour = symbol_colour),
    size = 2.15,
    fontface = "bold",
    show.legend = FALSE
  ) +
  scale_colour_identity() +
  scale_fill_manual(
    values = status_cols,
    breaks = fill_breaks_fig2,
    limits = fill_breaks_fig2,
    labels = fill_labels_fig2,
    drop = FALSE,
    guide = "none"
  ) +
  scale_x_discrete(labels = algorithm_labels, position = "top") +
  scale_y_discrete(limits = rev(category_levels)) +
  labs(title = "Course algorithm coverage", tag = "a", x = NULL, y = NULL) +
  coord_cartesian(clip = "off") +
  theme(
    axis.text.x = element_text(size = 5.6, lineheight = 0.88, margin = margin(b = 2.0)),
    axis.text.y = element_text(size = 6.0, margin = margin(r = 3.0)),
    legend.position = "bottom",
    plot.margin = margin(4, 2, 1, 2)
  )

source_long <- coverage_plot %>%
  select(algorithm, kat_code, library_code, vector_source, library_reference) %>%
  pivot_longer(
    c(kat_code, library_code),
    names_to = "evidence_type",
    values_to = "evidence_code"
  ) %>%
  mutate(
    full_reference = if_else(evidence_type == "kat_code", vector_source, library_reference),
    evidence_type = recode(
      evidence_type,
      kat_code = "KAT / standard",
      library_code = "Reference library"
    ),
    evidence_type = factor(evidence_type, levels = c("KAT / standard", "Reference library")),
    algorithm = factor(algorithm, levels = algorithm_levels),
    evidence_status = case_when(
      grepl("N/A|KAT-only|internal", full_reference) ~ "Limited",
      TRUE ~ "External"
    ),
    evidence_status = factor(evidence_status, levels = fill_breaks_fig2),
    text_colour = "#222222"
  )

p_references <- ggplot(source_long, aes(x = algorithm, y = evidence_type, fill = evidence_status)) +
  geom_tile(colour = "white", linewidth = 0.28, width = 0.94, height = 0.76) +
  geom_text(aes(label = evidence_code), size = 1.8, colour = "#222222", fontface = "bold") +
  scale_fill_manual(
    values = status_cols,
    breaks = fill_breaks_fig2,
    limits = fill_breaks_fig2,
    labels = fill_labels_fig2,
    drop = FALSE,
    guide = "none"
  ) +
  scale_x_discrete(labels = algorithm_labels, position = "top") +
  labs(title = "Reference and test-vector evidence", tag = "b", x = NULL, y = NULL) +
  theme(
    axis.text.x = element_blank(),
    axis.text.y = element_text(size = 6.0, margin = margin(r = 3.0)),
    legend.position = "bottom",
    plot.margin = margin(1, 2, 2, 2)
  )

reference_key <- paste(
  "Reference keys: K1 RFC4648; K2 RFC3629/Unicode; K3 FIPS180-4/RFC; K4 NIST/RFC; K5 RFC2202/4231.",
  "\nK6 PBKDF2 RFC vectors; K7 FIPS197/NIST SP800-38A/38D; K8 GB/T32907; K9 RC6 vectors;",
  "K10 RFC8017; K11 secp160r1; K12 RFC6979.",
  "\nLibrary keys: L1 Python stdlib; L2 hashlib/hmac; L3 cryptography; L4 gmssl; L5 internal or KAT-only;",
  "\u2014 no third-party reference."
)

legend_df <- tibble::tibble(
  x = c(1.0, 2.25, 3.95, 6.0, 8.25),
  status = factor(fill_breaks_fig2, levels = fill_breaks_fig2),
  label = fill_labels_fig2
)

p_legend <- ggplot(legend_df, aes(x = x, y = 1, fill = status)) +
  geom_tile(width = 0.16, height = 0.26, colour = NA) +
  geom_text(aes(x = x + 0.23, label = label), hjust = 0, size = 1.95, colour = "#222222") +
  scale_fill_manual(values = status_cols, guide = "none") +
  scale_x_continuous(limits = c(0.75, 10.4), expand = c(0, 0)) +
  scale_y_continuous(limits = c(0.78, 1.22), expand = c(0, 0)) +
  theme_void(base_family = "Arial") +
  labs(tag = NULL) +
  theme(plot.margin = margin(0, 2, 0, 2))

fig <- (p_coverage / p_references / p_legend) +
  plot_layout(heights = c(1.15, 0.9, 0.13)) +
  plot_annotation(
    title = "Algorithm coverage and validation references",
    caption = reference_key,
    theme = theme(
      plot.title = element_text(size = 8.6, face = "bold", hjust = 0, margin = margin(b = 3)),
      plot.caption = element_text(size = 4.8, hjust = 0, lineheight = 0.94, colour = "#444444"),
      plot.tag = element_text(size = 8, face = "bold", colour = "#111111"),
      plot.tag.position = c(0, 1)
    )
  ) &
  theme(
    legend.position = "bottom",
    legend.justification = "center",
    legend.box.margin = margin(0, 0, 0, 0)
  )

save_journal(fig, file.path(fig_dir, "fig2_algorithm_coverage_refined"), width_mm = 183, height_mm = 132, dpi = 450)
