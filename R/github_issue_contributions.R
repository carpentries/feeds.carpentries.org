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

  if (is.null(names(issues[[1]]))) {
    return(tibble::tibble())
  }

  issues %>%
    purrr::map_df(function(.x) {
      list(
        url = .x$html_url,
        title = .x$title,
        labels = purrr::map_chr(.x$labels, "name") %>% paste(., collapse = ","),
        label_colors = purrr::map_chr(.x$labels, "color") %>% paste(., collapse = ", "),
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
      repo = repo
    )
}

list_help_wanted <- purrr::map_df(
  c("datacarpentry", "swcarpentry", "librarycarpentry",
    "carpentrieslab", "carpentries-incubator"),
  ~ get_list_repos(.) %>%
    purrr::pmap_df(function(carpentries_org, repo, ...) {
      message("  repo: ", repo, appendLF = FALSE)
      res <- get_gh_issues(
        owner = carpentries_org, repo = repo, labels = "help wanted"
      )
      message(" -- n issues: ", nrow(res))
      res
    })
)

jsonlite::write_json(list_help_wanted, "_data/help_wanted_issues.json")
