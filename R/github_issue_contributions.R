source("R/utils.R")

get_gh_issues_raw <- function(owner, repo, labels) {
  if (!is.null(labels)) {
    stopifnot(identical(length(labels), 1L))
  }
  gh::gh(
    "GET /repos/:owner/:repo/issues",
    owner = owner,
    repo = repo,
    labels = labels
  )
}

extract_issue_info <- function(issues) {

  if (is.null(names(issues)) || is.null(names(issues[[1]]))) {
    return(tibble::tibble())
  }

  issues %>%
    purrr::map_df(function(.x) {
      list(
        url = .x$html_url,
        title = .x$title,
        type = dplyr::case_when(
          grepl("/pull/[0-9]+$", .x$html_url) ~ "PR",
          TRUE ~ "issue"
        ),
        labels = purrr::map_chr(.x$labels, "name") %>%
          paste(., collapse = ","),
        label_colors = purrr::map_chr(.x$labels, "color") %>%
          paste0("#", ., collapse = ","),
        font_colors = purrr::map_chr(.x$labels, "color") %>%
          paste0("#", .) %>%
          font_color(.) %>%
          paste(., collapse = ","),
        created_at = .x$created_at,
        updated_at = .x$updated_at
      )
    })
}

get_gh_issues <- function(owner, repo, labels) {
  get_gh_issues_raw(owner, repo, labels) %>%
    extract_issue_info() %>%
    dplyr::mutate(
      org = owner,
      repo = repo,
      full_repo = paste0(owner, "/", repo)
    )
}

list_organizations <- c(
  "Data Carpentry" = "datacarpentry",
  "Software Carpentry" = "swcarpentry",
  "Library Carpentry" = "librarycarpentry",
  "CarpentriesLab" = "carpentrieslab",
  "The Carpentries Incubator" = "carpentries-incubator"
)

list_help_wanted <- purrr::imap_dfr(
  list_organizations,
  ~ get_list_repos(
    .x, ignore_archived = TRUE,
    ignore_pattern = "^\\d{4}-\\d{2}-\\d{2}"
  ) %>%
    purrr::pmap_df(function(carpentries_org, repo, description, ...) {
      message("  repo: ", repo, appendLF = FALSE)
      res <- get_gh_issues(
        owner = carpentries_org, repo = repo, labels = "help wanted"
      )
      message(" -- n issues: ", nrow(res))
      res %>%
        dplyr::mutate(
          description = description,
          ## remove GitHub emoji from repo description
          clean_description = gsub(":([a-z0-9_]+):", "", description),
          org_name = .y)
    })
)

jsonlite::write_json(list_help_wanted, "_data/help_wanted_issues.json")
