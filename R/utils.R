library(gh)
library(jsonlite)
library(purrr)

`%<<%` <- function(x, y) {
  if (identical(length(x), 0L)) return(y)
  if (is.null(x) || identical(x, "") ||
        is.na(x)) return(y)
  x
}


get_list_repos <- function(org, ignore_archived = FALSE,
                           ignore_pattern = NULL, ...) {

  init_res  <- gh::gh("GET /orgs/:org/repos", org = org)
  res <- list()
  test <- TRUE
  i <- 1

  while (test) {
    message("Getting page: ", i, " for ", sQuote(org))
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

  res <- purrr::map_df(res, function(.x) {
    list(
      carpentries_org = .x$owner$login %<<% "",
      repo = .x$name,
      repo_url = .x$html_url,
      full_name = .x$full_name,
      description = .x$description %<<% "",
      rendered_site = .x$homepage %<<% "",
      private = .x$private,
      archived = .x$archived
    )
  }) %>%
    dplyr::filter(
      !private,
      carpentries_org == org,
      )

  if (ignore_archived) {
    res  <- res %>%
      dplyr::filter(!archived)
  }

  if (!is.null(ignore_pattern)) {
    res <- res %>%
      dplyr::filter(!grepl(ignore_pattern, repo, ...))
  }
  
  res %>%
    dplyr::select(-archived)
}


font_color <- function(hexcode) {
  rgb <- colorspace::hex2RGB(hexcode)
  rgbR <- rgb@coords[, "R"]
  rgbG <- rgb@coords[, "G"]
  rgbB <- rgb@coords[, "B"]
  luma <- ((0.299 * rgbR) + (0.587 * rgbG) + (0.114 * rgbB))
  res <- rep("#ffffff", length(hexcode))
  res[luma > .5] <- "#222222"
  res
}
