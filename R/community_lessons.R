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
