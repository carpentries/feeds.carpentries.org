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

get_github_topics <- function(owner, repo) {
  res <- gh::gh(
    "GET /repos/:owner/:repo/topics",
    owner = owner, repo = repo,
    .send_headers = c("Accept" = "application/vnd.github.mercy-preview+json")
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

make_community_lessons_feed <- function(path, ...) {

  carp_inc <- get_org_topics("carpentries-incubator")
  carp_lab <- get_org_topics("carpentrieslab")

  dplyr::bind_rows(carp_inc, carp_lab) %>%
    dplyr::select(-private) %>%
    dplyr::filter(grepl("lesson", github_topics)) %>%
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
    ) %>%
    jsonlite::write_json(path = path)

}

make_community_lessons_feed("_data/community_lessons.json")
