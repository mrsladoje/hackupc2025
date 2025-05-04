package com.pumpaj.evropo.service;

import com.fasterxml.jackson.databind.node.ObjectNode;
import com.pumpaj.evropo.model.Protest;
import com.pumpaj.evropo.model.Day;
import com.pumpaj.evropo.repository.ProtestRepository;
import com.pumpaj.evropo.repository.DayRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class DataProcessingService {

    private final ProtestRepository protestRepository;
    private final DayRepository dayRepository;

    @Autowired
    public DataProcessingService(ProtestRepository protestRepository, DayRepository dayRepository) {
        this.protestRepository = protestRepository;
        this.dayRepository = dayRepository;
    }

    /**
     * Process protest JSON data
     * Checks if protest exists using organizer, location, and date as unique identifiers
     * If it exists, updates with new information
     * If it doesn't exist, creates a new protest record
     */
    public void processProtestJson(ObjectNode protestJson) {
        String organizer = protestJson.path("organizer").asText();
        String location = protestJson.path("location").asText();
        String date = standardizeDate(protestJson.path("date").asText());

        // Check if all required fields are present
        if (organizer.isEmpty() || location.isEmpty() || date.isEmpty()) {
            System.out.println("Protest JSON missing required fields. Skipping.");
            return;
        }

        Optional<Protest> existingProtest = protestRepository.findByOrganizerAndLocationAndDate(organizer, location, date);

        if (existingProtest.isPresent()) {
            // Update existing protest with new information
            Protest protest = existingProtest.get();

            // Update count if it exists in the JSON and not in the database
            if (protestJson.has("count")) {
                ObjectNode countNode = (ObjectNode) protestJson.path("count");
                if (protest.getCount() == null) {
                    Protest.Count count = new Protest.Count();

                    if (countNode.has("government") && !countNode.path("government").isNull()) {
                        count.setGovernment(countNode.path("government").asInt());
                    }

                    if (countNode.has("independent") && !countNode.path("independent").isNull()) {
                        count.setIndependent(countNode.path("independent").asInt());
                    }

                    protest.setCount(count);
                } else {
                    Protest.Count count = protest.getCount();

                    if (count.getGovernment() == null && countNode.has("government") && !countNode.path("government").isNull()) {
                        count.setGovernment(countNode.path("government").asInt());
                    }

                    if (count.getIndependent() == null && countNode.has("independent") && !countNode.path("independent").isNull()) {
                        count.setIndependent(countNode.path("independent").asInt());
                    }
                }
            }

            // Update coordinates if they exist in the JSON and not in the database
            if (protest.getX() == null && protestJson.has("x") && !protestJson.path("x").isNull()) {
                protest.setX(protestJson.path("x").asDouble());
            }

            if (protest.getY() == null && protestJson.has("y") && !protestJson.path("y").isNull()) {
                protest.setY(protestJson.path("y").asDouble());
            }

            protestRepository.save(protest);
            System.out.println("Updated existing protest: " + organizer + ", " + location + ", " + date);
        } else {
            // Create new protest
            Protest protest = new Protest();
            protest.setOrganizer(organizer);
            protest.setLocation(location);
            protest.setDate(date);

            // Set count if it exists in the JSON
            if (protestJson.has("count")) {
                ObjectNode countNode = (ObjectNode) protestJson.path("count");
                Protest.Count count = new Protest.Count();

                if (countNode.has("government") && !countNode.path("government").isNull()) {
                    count.setGovernment(countNode.path("government").asInt());
                }

                if (countNode.has("independent") && !countNode.path("independent").isNull()) {
                    count.setIndependent(countNode.path("independent").asInt());
                }

                protest.setCount(count);
            }

            // Set coordinates if they exist in the JSON
            if (protestJson.has("x") && !protestJson.path("x").isNull()) {
                protest.setX(protestJson.path("x").asDouble());
            }

            if (protestJson.has("y") && !protestJson.path("y").isNull()) {
                protest.setY(protestJson.path("y").asDouble());
            }

            protestRepository.save(protest);
            System.out.println("Created new protest: " + organizer + ", " + location + ", " + date);
        }
    }

    /**
     * Process day JSON data
     * Checks if day record exists using date as unique identifier
     * If it exists, adds the values from the JSON to the existing values
     * If it doesn't exist, creates a new day record
     */
    public void processDayJson(ObjectNode dayJson) {
        String date = standardizeDate(dayJson.path("date").asText());

        if (date.isEmpty()) {
            System.out.println("Day JSON missing required date field. Skipping.");
            return;
        }

        Optional<Day> existingDay = dayRepository.findByDate(date);

        if (existingDay.isPresent()) {
            // Update existing day by adding values
            Day day = existingDay.get();

            // Update state driven messaging
            if (dayJson.has("state_driven_messaging") && !dayJson.path("state_driven_messaging").isNull()) {
                Integer currentValue = day.getStateDrivenMessaging();
                if (currentValue == null) {
                    currentValue = 0;
                }
                day.setStateDrivenMessaging(currentValue + dayJson.path("state_driven_messaging").asInt());
            }

            // Update pro student messaging
            if (dayJson.has("pro_student_messaging") && !dayJson.path("pro_student_messaging").isNull()) {
                Integer currentValue = day.getProStudentMessaging();
                if (currentValue == null) {
                    currentValue = 0;
                }
                day.setProStudentMessaging(currentValue + dayJson.path("pro_student_messaging").asInt());
            }

            // Update student mentions
            if (dayJson.has("student_mentions")) {
                ObjectNode mentionsNode = (ObjectNode) dayJson.path("student_mentions");

                if (day.getStudentMentions() == null) {
                    day.setStudentMentions(new Day.StudentMentions());
                }

                Day.StudentMentions mentions = day.getStudentMentions();

                if (mentionsNode.has("good_count") && !mentionsNode.path("good_count").isNull()) {
                    Integer currentValue = mentions.getGoodCount();
                    if (currentValue == null) {
                        currentValue = 0;
                    }
                    mentions.setGoodCount(currentValue + mentionsNode.path("good_count").asInt());
                }

                if (mentionsNode.has("bad_count") && !mentionsNode.path("bad_count").isNull()) {
                    Integer currentValue = mentions.getBadCount();
                    if (currentValue == null) {
                        currentValue = 0;
                    }
                    mentions.setBadCount(currentValue + mentionsNode.path("bad_count").asInt());
                }
            }

            // Update state mentions
            if (dayJson.has("state_mentions")) {
                ObjectNode mentionsNode = (ObjectNode) dayJson.path("state_mentions");

                if (day.getStateMentions() == null) {
                    day.setStateMentions(new Day.StateMentions());
                }

                Day.StateMentions mentions = day.getStateMentions();

                if (mentionsNode.has("good_count") && !mentionsNode.path("good_count").isNull()) {
                    Integer currentValue = mentions.getGoodCount();
                    if (currentValue == null) {
                        currentValue = 0;
                    }
                    mentions.setGoodCount(currentValue + mentionsNode.path("good_count").asInt());
                }

                if (mentionsNode.has("bad_count") && !mentionsNode.path("bad_count").isNull()) {
                    Integer currentValue = mentions.getBadCount();
                    if (currentValue == null) {
                        currentValue = 0;
                    }
                    mentions.setBadCount(currentValue + mentionsNode.path("bad_count").asInt());
                }
            }

            // Update propaganda count
            if (dayJson.has("propaganda_count") && !dayJson.path("propaganda_count").isNull()) {
                Integer currentValue = day.getPropagandaCount();
                if (currentValue == null) {
                    currentValue = 0;
                }
                day.setPropagandaCount(currentValue + dayJson.path("propaganda_count").asInt());
            }

            // Update pro protest count
            if (dayJson.has("pro_protest_count") && !dayJson.path("pro_protest_count").isNull()) {
                Integer currentValue = day.getProProtestCount();
                if (currentValue == null) {
                    currentValue = 0;
                }
                day.setProProtestCount(currentValue + dayJson.path("pro_protest_count").asInt());
            }

            dayRepository.save(day);
        } else {
            // Create new day
            Day day = new Day();
            day.setDate(date);

            // Set state driven messaging
            if (dayJson.has("state_driven_messaging") && !dayJson.path("state_driven_messaging").isNull()) {
                day.setStateDrivenMessaging(dayJson.path("state_driven_messaging").asInt());
            }

            // Set pro student messaging
            if (dayJson.has("pro_student_messaging") && !dayJson.path("pro_student_messaging").isNull()) {
                day.setProStudentMessaging(dayJson.path("pro_student_messaging").asInt());
            }

            // Set student mentions
            if (dayJson.has("student_mentions")) {
                ObjectNode mentionsNode = (ObjectNode) dayJson.path("student_mentions");
                Day.StudentMentions mentions = new Day.StudentMentions();

                if (mentionsNode.has("good_count") && !mentionsNode.path("good_count").isNull()) {
                    mentions.setGoodCount(mentionsNode.path("good_count").asInt());
                }

                if (mentionsNode.has("bad_count") && !mentionsNode.path("bad_count").isNull()) {
                    mentions.setBadCount(mentionsNode.path("bad_count").asInt());
                }

                day.setStudentMentions(mentions);
            }

            // Set state mentions
            if (dayJson.has("state_mentions")) {
                ObjectNode mentionsNode = (ObjectNode) dayJson.path("state_mentions");
                Day.StateMentions mentions = new Day.StateMentions();

                if (mentionsNode.has("good_count") && !mentionsNode.path("good_count").isNull()) {
                    mentions.setGoodCount(mentionsNode.path("good_count").asInt());
                }

                if (mentionsNode.has("bad_count") && !mentionsNode.path("bad_count").isNull()) {
                    mentions.setBadCount(mentionsNode.path("bad_count").asInt());
                }

                day.setStateMentions(mentions);
            }

            // Set propaganda count
            if (dayJson.has("propaganda_count") && !dayJson.path("propaganda_count").isNull()) {
                day.setPropagandaCount(dayJson.path("propaganda_count").asInt());
            }

            // Set pro protest count
            if (dayJson.has("pro_protest_count") && !dayJson.path("pro_protest_count").isNull()) {
                day.setProProtestCount(dayJson.path("pro_protest_count").asInt());
            }

            dayRepository.save(day);
        }
    }

    /**
     * Standardizes date format to YYYY-MM-DD
     * Handles input formats like DD.MM.YYYY or D.M.YYYY (with or without trailing dot)
     */
    private String standardizeDate(String dateString) {
        // If the date is already in YYYY-MM-DD format, return it as is
        if (dateString.matches("\\d{4}-\\d{2}-\\d{2}")) {
            return dateString;
        }

        // Check if it's in DD.MM.YYYY format
        // The pattern allows for optional trailing dot and single-digit day/month
        if (dateString.matches("\\d{1,2}\\.\\d{1,2}\\.\\d{4}\\.?")) {
            // Remove trailing dot if present
            if (dateString.endsWith(".")) {
                dateString = dateString.substring(0, dateString.length() - 1);
            }

            // Split by dots
            String[] parts = dateString.split("\\.");
            if (parts.length == 3) {
                // Ensure day and month have two digits
                String day = parts[0].length() == 1 ? "0" + parts[0] : parts[0];
                String month = parts[1].length() == 1 ? "0" + parts[1] : parts[1];
                String year = parts[2];

                // Return in YYYY-MM-DD format
                return year + "-" + month + "-" + day;
            }
        }

        // If format is unknown, return original string
        System.out.println("Warning: Could not standardize date format for: " + dateString);
        return dateString;
    }
}