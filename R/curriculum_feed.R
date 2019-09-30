library(gh)
library(jsonlite)
library(purrr)

`%<<%` <- function(x, y) {
  if (identical(length(x), 0L)) return(y)
  if (is.null(x) || identical(x, "") ||
        is.na(x)) return(y)
  x
}

get_github_topics <- function(owner, repo) {
  res <- gh::gh(
    "GET /repos/:owner/:repo/topics",
    owner = owner, repo = repo,
    .send_headers = c("Accept" = "application/vnd.github.mercy-preview+json")
  )

  purrr::map_chr(res[["names"]], ~ .)
}

get_list_repos <- function(org) {

  init_res  <- gh::gh("GET /orgs/:org/repos", org = org)
  res <- list()
  test <- TRUE
  i <- 1

  while (test) {
    message("Getting page: ", i)
    res <- append(res, init_res)

    init_res <- tryCatch({
      gh::gh_next(init_res)
    },
    error = function(e) {
      test <<- FALSE
      NULL
    })
    i <- i+1
  }

  purrr::map_df(res, function(.x) {
    list(
      owner = .x$owner$login %<<% "",
      repo = .x$name,
      full_name = .x$full_name,
      description = .x$description %<<% "",
      rendered_site = .x$homepage %<<% "",
      private = .x$private
    )
  }) %>%
     dplyr::filter(
       !private,
       owner == org
     ) %>%
    dplyr::mutate(
      github_topics = purrr::pmap(., function(owner, repo, ...) {
        get_github_topics(owner, repo) %<<% ""
      })
    )
}

make_incubator_feed <- function(path, ...) {

  get_list_repos("carpentries-incubator") %>%
    dplyr::select(-private) %>%
    filter(grepl("lesson", github_topics)) %>%
    jsonlite::write_json(path = path)


}

make_incubator_feed("_data/incubator_feed.json")
