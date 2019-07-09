library(readr)
library(dplyr)
library(tidyr)
library(plotly)
library(ggplot2)
library(htmlwidgets)
library(countrycode)
library(maps)
library(svglite)

check_for_na <- function(.data, ...) {
  test <- pull(.data, ...) %>%
    is.na() %>%
    any()

  if (test) {
    stop("found NAs, is there a new workshop type?")
  }

  .data
}

check_export_dir <- function(file) {
  if (!dir.exists(dirname(file))) {
    stop(
      "directory: ", dirname(file),
      " doesn't exist. Create it before using this function."
    )
  }
}

export_ggplotly <- function(plot, file) {

  tmp_file <- basename(file)
  res <- saveWidget(plot, file = tmp_file)
  file.rename(tmp_file, file)

}

## function to create summary by workshops by date and by type,
## including total number of workshops
prepare_workshops_through_time <- function(wksp_data) {
  summary_by_type <- wksp_data %>%
    count(tag_name, end_date) %>%
    ungroup(tag_name)

  summary_total <- wksp_data %>%
    count(end_date) %>%
    mutate(tag_name = "Total") %>%
    ungroup(tag_name)

  summary_through_time <- bind_rows(
    summary_by_type,
    summary_total
  ) %>%
    mutate(tag_name = case_when(
      tag_name == "SWC" ~ "Software Carpentry",
      tag_name == "DC" ~ "Data Carpentry",
      tag_name == "LC" ~ "Library Carpentry",
      tag_name == "TTT" ~ "Instructor Training",
      tag_name == "Total" ~ "Total"
    )) %>%
    group_by(tag_name) %>%
    mutate(n_total = cumsum(n)) %>%
    check_for_na(tag_name) %>%
    ungroup(tag_name)
}

workshops_through_time <- function(wksp_data, outfile = "./plot_workshops_through_time.html") {

  check_export_dir(outfile)

  summary_through_time <- prepare_workshops_through_time(wksp_data)

  plot_summary <- summary_through_time %>%
    ggplot(aes(x = end_date, y = n_total, group = tag_name, colour = tag_name)) +
    geom_line() +
    scale_color_viridis_d(name = "Workshop type", end = .95) +
    labs(
      title = "Number of workshops through time",
      x = "Date",
      y = "Number of Workshops"
    )

  res_plot <- ggplotly(plot_summary)

  export_ggplotly(res_plot, outfile)

  outfile
}

workshops_by_year <- function(wksp_data, outfile = "./plot_workshops_by_year.html") {
  check_export_dir(outfile)

  summary_per_year <- prepare_workshops_through_time(wksp_data) %>%
    mutate(year = format(.data$end_date, "%Y")) %>%
    group_by(year, tag_name)  %>%
    summarize(
      n = sum(n)
    ) %>%
    complete(year, tag_name, fill = list(n = 0))

  plot_per_year <- ggplot(summary_per_year) +
    geom_col(aes(x = year, y = n, fill = reorder(tag_name, n)),
      position = "dodge") +
    scale_fill_viridis_d(name = "Workshop type", end = .95) +
    labs(
      title = "Number of workshops per year",
      x = "Year",
      y = "Number of Workshops"
    )

  res_plot <- ggplotly(plot_per_year)

  export_ggplotly(res_plot, outfile)

  outfile

}

workshops_map <- function(wksp_data, outfile = "./plot_workshops_map.svg") {

  check_export_dir(outfile)

  wksp_data <- wksp_data %>%
    filter(latitude < 90) %>%
    mutate(year = format(start_date, "%Y"))

  wksp_data_no_online <- wksp_data %>%
    filter(country != "W3" &
             !grepl("online", tag_name)) %>%
    mutate(country_name = countrycode(
      country,
      "iso2c",
      "country.name"
    ))

  wksp_map_points <- wksp_data_no_online %>%
    mutate(coords = paste(latitude, longitude, sep = "|")) %>%
    group_by(coords) %>%
    mutate(n_loc = n()) %>%
    ungroup() %>%
    distinct(latitude, longitude, n_loc)

  summ_by_country <- wksp_data_no_online %>%
    count(country_name) %>%
    complete(country_name, fill = list(n = 0))


  world <- map_data("world") %>%
    mutate(region_2 = countrycode::countrycode(
      region,
      "country.name",
      "country.name"
    )) %>%
    left_join(summ_by_country, by = c("region_2" = "country_name"))

  map <- ggplot() +
    geom_map(aes(fill = n, x = long, y = lat, map_id = region),
      data = world, map = world)  +
    scale_fill_viridis_c(na.value = "gray70",
      breaks = c(1, 10, 100, 500),
      trans = "log", name = "Number of Workshops") +
    scale_size(name = "Number of workshops") +
    geom_point(data = wksp_map_points,
      aes(x = longitude, y = latitude, size = n_loc),
      color = "coral",
      inherit.aes = FALSE) +
    coord_quickmap() +
    theme_minimal() +
    theme(legend.position = "bottom") +
    labs(
      x = "", y = ""
    ) +
    scale_color_identity(guide = FALSE)

  svglite::svglite(file = outfile, width = 1600/72, height = 900/72)
  print(map)
  dev.off()


  outfile
}


wksp <- read_csv("https://data.softwarecarpentry.org/api/queries/125/results.csv?api_key=ef7xp02JqDvg7JkEbxbElfg8ICgBaQEaXnz0NhQS") %>%
  mutate(tag_name = gsub(",(unresponsive|online)", "", tag_name)) %>%
  filter(
    end_date <= Sys.Date(),
    tag_name %in% c("SWC", "LC", "DC", "TTT")
  )

message("working directory: ", getwd())

workshops_through_time(wksp)
workshops_by_year(wksp)
workshops_map(wksp)
