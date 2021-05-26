source("R/utils.R")

LIFE_CYCLE_TAGS <- c("pre-alpha", "alpha", "beta", "stable")
COMMON_TAGS <- c(
  "carpentries",
  "carpentries-incubator",
  "carpentries-lesson",
  "carpentryconnect",
  "data-carpentry",
  "datacarpentry",
  "education",
  "lesson"
)

check_missing_repo_info <- function(.d, field) {
  if (any(!nzchar(.d[[field]]))) {
    paste0(
      "Missing repo ", sQuote(field), " for: \n",
      paste0("  - ", .d$repo_url[!nzchar(.d[[field]])], collapse = "\n"),
      "\n"
    )
  }
}

check_repo_info <- function(.d, fields) {
  tryCatch({
    out <- purrr::map(
      fields, ~ check_missing_repo_info(.d, .)
    )
    msgs <- purrr::keep(out, ~ !is.null(.))

    if (length(msgs)) {
      stop(msgs, call. = FALSE)
    }

    cli::cli_alert_success("No issues detected!")
  },
  error = function(err) {
    stop(err$message, call. = FALSE)
  })
}

make_community_lessons_feed <- function(path, ...) {

  carp_inc <- get_org_topics("carpentries-incubator")
  carp_lab <- get_org_topics("carpentrieslab")

  res <- dplyr::bind_rows(carp_inc, carp_lab) %>%
    dplyr::select(-private) %>%
    dplyr::filter(grepl("lesson", github_topics)) %>%
    dplyr::mutate(
      org_full_name = purrr::map_chr(.data$carpentries_org, expand_full_name)
    ) %>%
    extract_tag(
      life_cycle_tag,
      LIFE_CYCLE_TAGS,
      approach = "include",
      allow_multiple = FALSE,
      allow_empty = FALSE
    ) %>%
    extract_tag(
      lesson_tags,
      COMMON_TAGS,
      approach = "exclude",
      allow_multiple = TRUE,
      allow_empty = TRUE
    )

  ## checks
  check_repo_info(res, c("description", "rendered_site"))

  res %>%
    jsonlite::write_json(path = path)

}

make_community_lessons_feed("_data/community_lessons.json")
