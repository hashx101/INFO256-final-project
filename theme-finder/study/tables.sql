DROP TABLE IF EXISTS `st_task_log`;
CREATE  TABLE `st_task_log` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `participant_id` VARCHAR(45) NOT NULL ,
  `task_number` INT NOT NULL ,
  `interface_type` VARCHAR(45) NULL ,
  `theme_number` INT NULL ,
  `time_in_s` INT NULL ,
  `number_of_sentences` INT NULL ,
  PRIMARY KEY (`id`, `participant_id`, `task_number`) );

 DROP TABLE IF EXISTS `st_relevant_sentences`;
CREATE  TABLE `st_relevant_sentences` (
    `participant_id` VARCHAR(45) NOT NULL ,
    `task_number` INT NOT NULL ,
    `sentence_id` INT NOT NULL,
    PRIMARY KEY (`participant_id`, `task_number`, `sentence_id`) );

DROP TABLE IF EXISTS `st_self_evaluation`;
CREATE  TABLE `st_self_evaluation` (
    `participant_id` VARCHAR(45) NOT NULL ,
    `task_number` INT NOT NULL ,
    `understanding` INT NOT NULL,
    `theme_understanding` INT NOT NULL,
    `performance` INT NOT NULL,
    `difficulty` INT NOT NULL,
    PRIMARY KEY (`participant_id`, `task_number`, `understanding`, 
        `theme_understanding`, `performance`, `difficulty`) );

DROP TABLE IF EXISTS `st_participant_background`;
CREATE  TABLE `st_participant_background` (
    `participant_id` VARCHAR(45) NOT NULL ,
    `background` VARCHAR(45) NOT NULL,
    PRIMARY KEY (`participant_id`, `background`) );

DROP TABLE IF EXISTS `st_activity_log`;
CREATE  TABLE `st_activity_log` (
    `id` INT NOT NULL AUTO_INCREMENT ,
    `participant_id` VARCHAR(45) NOT NULL ,
    `task_number` VARCHAR(45) NOT NULL,
    `activity` VARCHAR(45) NOT NULL,
    `search_query` VARCHAR(100) NULL,
    `num_relevant` INT NULL,
    `num_irrelevant` INT NULL,
    PRIMARY KEY (`id`, `participant_id`, `task_number`, `activity`) );

DROP TABLE IF EXISTS `st_expert_scores`;
CREATE  TABLE `st_expert_scores` (
    `id` INT NOT NULL AUTO_INCREMENT ,
    `theme_number` INT NOT NULL ,
    `sentence_id` INT NOT NULL,
    `is_relevant` INT NULL,
    PRIMARY KEY (`id`, `theme_number`, `sentence_id`));