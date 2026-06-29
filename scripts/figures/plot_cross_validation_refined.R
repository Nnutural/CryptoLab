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

save_journal <- function(plot, filename, width_mm = 183, height_mm = 142, dpi = 450) {
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
layer_levels <- c(
  "KAT standard vectors",
  "Third-party reference",
  "HTTP API tests",
  "Frontend build/integration",
  "Verbose/demo support"
)
layer_labels <- c(
  "KAT standard vectors" = "KAT standard\nvectors",
  "Third-party reference" = "Third-party\nreference",
  "HTTP API tests" = "HTTP API\ntests",
  "Frontend build/integration" = "Frontend /\nintegration",
  "Verbose/demo support" = "Verbose /\ndemo support"
)

status_breaks <- c("Pass", "Partial", "No evidence")
status_labels <- c("Pass", "Partial", "No evidence")

evidence_plot <- evidence %>%
  mutate(
    algorithm = factor(algorithm, levels = rev(algorithm_levels)),
    evidence_layer = factor(evidence_layer, levels = layer_levels),
    status_label = factor(status_label, levels = status_breaks),
    status_symbol = case_when(
      status_label == "Pass" ~ "\u2713",
      status_label == "Partial" ~ "Part.",
      TRUE ~ "\u2014"
    ),
    symbol_colour = case_when(
      status_label == "Pass" ~ "white",
      status_label == "Partial" ~ "#222222",
      TRUE ~ "#555555"
    )
  )

write_csv(evidence_plot, file.path(data_dir, "fig3_cross_validation_refined.csv"))

p_matrix <- ggplot(evidence_plot, aes(x = evidence_layer, y = algorithm, fill = status_label)) +
  geom_tile(colour = "white", linewidth = 0.30, width = 0.94, height = 0.84) +
  geom_text(
    aes(label = status_symbol, colour = symbol_colour),
    size = 2.10,
    fontface = "bold",
    show.legend = FALSE
  ) +
  scale_colour_identity() +
  scale_fill_manual(
    values = status_cols,
    breaks = status_breaks,
    limits = status_breaks,
    labels = status_labels,
    drop = FALSE,
    guide = "none"
  ) +
  scale_x_discrete(labels = layer_labels, position = "top") +
  labs(title = "Evidence layers by algorithm family", x = NULL, y = NULL) +
  coord_cartesian(clip = "off") +
  theme(
    axis.text.x = element_text(size = 6.0, lineheight = 0.88, margin = margin(b = 2)),
    axis.text.y = element_text(size = 6.0, margin = margin(r = 3)),
    legend.position = "bottom",
    plot.margin = margin(4, 2, 2, 2)
  )

summary_counts <- evidence_plot %>%
  count(evidence_layer, status_label, .drop = FALSE) %>%
  mutate(
    status_label = factor(status_label, levels = status_breaks),
    stack_order = case_when(
      status_label == "No evidence" ~ 1L,
      status_label == "Partial" ~ 2L,
      status_label == "Pass" ~ 3L,
      TRUE ~ 4L
    )
  ) %>%
  group_by(evidence_layer) %>%
  arrange(stack_order, .by_group = TRUE) %>%
  mutate(
    x_id = as.integer(evidence_layer),
    ymin = cumsum(lag(n, default = 0)),
    ymax = cumsum(n),
    ymid = (ymin + ymax) / 2,
    label = if_else(n > 0, as.character(n), ""),
    label_colour = if_else(status_label == "Pass", "white", "#222222")
  ) %>%
  ungroup()

write_csv(summary_counts, file.path(data_dir, "fig3_cross_validation_refined_counts.csv"))

p_counts <- ggplot(summary_counts) +
  geom_rect(
    aes(
      xmin = x_id - 0.31,
      xmax = x_id + 0.31,
      ymin = ymin,
      ymax = ymax,
      fill = status_label
    ),
    colour = "white",
    linewidth = 0.28
  ) +
  geom_text(
    aes(x = x_id, y = ymid, label = label, colour = label_colour),
    size = 1.95,
    fontface = "bold",
    show.legend = FALSE
  ) +
  scale_colour_identity() +
  scale_fill_manual(
    values = status_cols,
    breaks = status_breaks,
    limits = status_breaks,
    labels = status_labels,
    drop = FALSE,
    guide = guide_legend(nrow = 1, byrow = TRUE)
  ) +
  scale_x_continuous(
    breaks = seq_along(layer_levels),
    labels = unname(layer_labels[layer_levels]),
    expand = expansion(add = 0.45)
  ) +
  scale_y_continuous(
    breaks = c(0, 5, 10),
    limits = c(0, 10),
    expand = expansion(mult = c(0, 0.035))
  ) +
  labs(title = "Evidence-cell counts", x = NULL, y = "Cells (count)") +
  theme(
    axis.line.y = element_line(linewidth = 0.30, colour = "#222222"),
    axis.text.x = element_text(size = 5.8, lineheight = 0.88, margin = margin(t = 2)),
    axis.text.y = element_text(size = 5.8),
    axis.title.y = element_text(size = 6.0, margin = margin(r = 3)),
    panel.grid.major.y = element_line(colour = "#ECECEC", linewidth = 0.25),
    legend.position = "none",
    plot.margin = margin(3, 2, 2, 2)
  )

fig <- (p_matrix / p_counts) +
  plot_layout(heights = c(1.65, 0.95)) +
  plot_annotation(
    title = "Cross-validation evidence across algorithms and validation layers",
    tag_levels = "a",
    theme = theme(
      plot.title = element_text(size = 8.6, face = "bold", hjust = 0, margin = margin(b = 3)),
      plot.tag = element_text(size = 8, face = "bold", colour = "#111111"),
      plot.tag.position = c(0, 1)
    )
  ) &
  theme(
    legend.position = "bottom",
    legend.justification = "center",
    legend.box.margin = margin(0, 0, 0, 0)
  )

save_journal(fig, file.path(fig_dir, "fig3_cross_validation_refined"), width_mm = 183, height_mm = 142, dpi = 450)
