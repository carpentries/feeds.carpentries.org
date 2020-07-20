### data feed for the repository information for the official lessons.
###
### Currently the curriculum is hard-coded, ideally we'd want this information
### to come from somewhere else.
###
### This script has a side effect to ensure that all repos with the 'lesson'
### github topic have the appropriate other topics (at least for life cycle and
### human languages).

source("R/utils.R")

LIFE_CYCLE_TAGS <- c("pre-alpha", "alpha", "beta", "stable", "on-hold")
HUMAN_LANGUAGE <- c("english", "spanish")

GITHUB_ORGS <- c(
  "carpentries",
  "datacarpentry",
  "swcarpentry",
  "librarycarpentry"
)

##' @param path the path (including file name) where the lesson feed need to be
##'   saved.k
make_lessons_feed <- function(path) {

  purrr::map_df(
    GITHUB_ORGS,
    get_org_topics
  )  %>%
    dplyr::filter(
      !private,
      purrr::map_lgl(github_topics, ~ "lesson" %in% .)
    ) %>%
    extract_tag(
      life_cycle_tag,
      LIFE_CYCLE_TAGS,
      approach = "include",
      allow_multiple = FALSE,
      allow_empty = FALSE
    ) %>%
    extract_tag(
      human_language,
      HUMAN_LANGUAGE,
      approach = "include",
      allow_multiple = FALSE,
      allow_empty = FALSE
    ) %>%
    dplyr::select(
      carpentries_org,
      repo,
      repo_url,
      description,
      rendered_site,
      life_cycle = life_cycle_tag,
      human_language,
      github_topics
    ) %>%
    dplyr::mutate(
      human_language = unlist(human_language),
      life_cycle = unlist(life_cycle)
    ) %>%
    jsonlite::write_json(path)

}


make_lessons_feed("_data/lessons.json")
