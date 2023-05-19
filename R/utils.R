library(gh)
library(jsonlite)
library(purrr)

#' Create a fallback pipe 
#' 
#' @param x an R object
#' @param y an R object to use if x is missing in some fashion
#'
#' @examples
#' "hello there" %<<% "goodbye" # says hello
#' sleep %<<% "no sleep data" # prints the sleep data set
#' 
#' # examples when this is useful: missing data
#' "" %<<% "missing data"
#' NULL %<<% "missing data"
#' character(0) %<<% "missing data" 
#' c(NA, NA) %<<% "missing data"
`%<<%` <- function(x, y) {
  if (identical(length(x), 0L)) {
    return(y)
  }
  all_missing <- is.null(x) || identical(x, "") || all(is.na(x))
  if (all_missing) {
    return(y)
  }
  x
}

use_pat <- function() {
  if (Sys.getenv("GITHUB_PAT") != "" || Sys.getenv("GITHUB_TOKEN") != "") {
    cli::cli_alert_success("Using GitHub token!")
  } else {
    cli::cli_alert_danger("No GitHub token detected.")
  }
}
use_pat()

check_rate_limit <- function() {
  res <- gh::gh("GET /user")

  rate_limit <- attr(res, "response")[["x-ratelimit-limit"]]
  rate_remaining <- attr(res, "response")[["x-ratelimit-remaining"]]
  reset_time <- lubridate::as_datetime(
    as.numeric(attr(res, "response")[["x-ratelimit-reset"]])
  )

  cli::cli_alert_info(
    paste("It remains", rate_remaining, "out of ", rate_limit)
  )
  cli::cli_alert_info(
    paste("Next reset at:", reset_time)
  )

}
## not available form GHA:
## check_rate_limit()

get_list_repos <- function(org, ignore_archived = FALSE,
                           ignore_pattern = NULL, ...) {

  res  <- gh::gh(
    "GET /orgs/:org/repos",
    org = org,
    per_page = 100,
    .limit = Inf,
    .send_headers = c(
      "If-Modified-Since" = six_hours_ago()
    )
  )
  # res <- list()
  # test <- TRUE
  # i <- 1

  # while (test) {
  #   message("Getting page: ", i, " for ", sQuote(org))
  #   res <- append(res, init_res)

  #   init_res <- tryCatch({
  #     gh::gh_next(init_res)
  #   },
  #   error = function(e) {
  #     test <<- FALSE
  #     NULL
  #   })
  #   i <- i+1
  # }

  res <- purrr::map_df(res, function(.x) {
    list(
      carpentries_org = tolower(.x$owner$login) %<<% "",
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
      tolower(carpentries_org) == tolower(org)
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


get_github_topics <- function(owner, repo) {
  res <- gh::gh(
    "GET /repos/:owner/:repo/topics",
    owner = owner, repo = repo,
    .send_headers = c(
      "Accept" = "application/vnd.github.mercy-preview+json",
      "If-Modified-Since" = six_hours_ago()
    )
  )

  purrr::map_chr(res[["names"]], ~ .)
}

get_org_topics <- function(org) {

  get_list_repos(org) %>%
    dplyr::filter(
      !private,
      carpentries_org == org
    ) %>%
    dplyr::mutate(
      github_topics = purrr::pmap(., function(carpentries_org, repo, ...) {
        get_github_topics(carpentries_org, repo) %<<% ""
      })
    )
}


##' @param data the data frame that contains the column `github_topics` from
##'   which the tags should be extracted
##' @param new_col_name name of the new column that will contain the extracted
##'   tags
##' @param dict the dictionary of tags (as a character vector) against which the
##'   content of the `github_topics` column will be compared
##' @param approach when set to `include` the tag(s) that match(es) the content
##'   of the vector specified in `dict` will be extracted to create the content
##'   of the new column; when set to `exclude` the tag(s) that match(es) the
##'   content of the vector specified in `dict` will be excluded to create the
##'   content of the new column. For instance if the column `github_topics` has
##'   the values `c("tag1", "tag2")` and `dict` is `"tag1"`, the new column will
##'   have the value `tag1` when using `include` and `tag2` when using
##'   `exclude`.
##' @param allow_multiple can the resulting new column contain more than one
##'   tag?
##' @param allow_empty can the resulting new column contain an empty value?
extract_tag <- function(data,
                        new_col_name,
                        dict,
                        approach = c("include", "exclude"),
                        allow_multiple,
                        allow_empty
                        ) {

  approach <- match.arg(approach)

  if (identical(approach, "include")) {
    f1 <- intersect
    f2 <- setdiff
  } else if (identical(approach, "exclude")) {
    f1 <- setdiff
    f2 <- intersect
  } else {
    stop("invalid value for approach")
  }

  data %>%
    dplyr::mutate(!!rlang::quo_name(rlang::enquo(new_col_name)) := purrr::pmap(.,
      function(github_topics, full_name, ...) {
        extracted_tag <- f1(github_topics, dict)
        if ((!allow_multiple) && length(extracted_tag) > 1) {
          stop("More than one tag detected for: ", full_name)
        }
        if (length(extracted_tag) == 0) {
          if (! allow_empty) {
            stop("No tag found among (", paste(dict, collapse = ", "), ") ",
              "for repo: ", full_name)
          }
          return("")
        }
        extracted_tag
      })) %>%
    dplyr::mutate(github_topics = purrr::pmap(., function(github_topics, ...) {
      f2(github_topics, dict)
    }))

}



## convert the name of the GitHub organization into the human version of the
## name of the organization.
expand_full_name <- function(org) {
  res <- dplyr::case_when(
    org == "carpentries" ~ "The Carpentries",
    org == "carpentries-incubator" ~ "The Carpentries Incubator",
    org == "carpentries-lab" ~ "The Carpentries Lab",
    org == "datacarpentry" ~ "Data Carpentry",
    org == "librarycarpentry" ~ "Library Carpentry",
    org == "swcarpentry" ~ "Software Carpentry",
    TRUE ~ NA_character_
  )

  if (is.na(res)) {
    stop("Unrecognized organization: ", sQuote(org), call. = FALSE)
  }

  res
}

six_hours_ago <- function() {
  lubridate::now() - lubridate::hours(6)
}
