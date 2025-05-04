package com.pumpaj.evropo.model;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.index.Indexed;

@Document(collection = "days")
public class Day {
    @Id
    private String id;

    @Indexed(unique = true)
    private String date;
    private Integer stateDrivenMessaging;
    private Integer proStudentMessaging;
    private StudentMentions studentMentions;
    private StateMentions stateMentions;
    private Integer propagandaCount;
    private Integer proProtestCount;

    public static class StudentMentions {
        private Integer goodCount;
        private Integer badCount;

        // Getters and setters
        public Integer getGoodCount() {
            return goodCount;
        }

        public void setGoodCount(Integer goodCount) {
            this.goodCount = goodCount;
        }

        public Integer getBadCount() {
            return badCount;
        }

        public void setBadCount(Integer badCount) {
            this.badCount = badCount;
        }
    }

    public static class StateMentions {
        private Integer goodCount;
        private Integer badCount;

        // Getters and setters
        public Integer getGoodCount() {
            return goodCount;
        }

        public void setGoodCount(Integer goodCount) {
            this.goodCount = goodCount;
        }

        public Integer getBadCount() {
            return badCount;
        }

        public void setBadCount(Integer badCount) {
            this.badCount = badCount;
        }
    }

    // Getters and setters
    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getDate() {
        return date;
    }

    public void setDate(String date) {
        this.date = date;
    }

    public Integer getStateDrivenMessaging() {
        return stateDrivenMessaging;
    }

    public void setStateDrivenMessaging(Integer stateDrivenMessaging) {
        this.stateDrivenMessaging = stateDrivenMessaging;
    }

    public Integer getProStudentMessaging() {
        return proStudentMessaging;
    }

    public void setProStudentMessaging(Integer proStudentMessaging) {
        this.proStudentMessaging = proStudentMessaging;
    }

    public StudentMentions getStudentMentions() {
        return studentMentions;
    }

    public void setStudentMentions(StudentMentions studentMentions) {
        this.studentMentions = studentMentions;
    }

    public StateMentions getStateMentions() {
        return stateMentions;
    }

    public void setStateMentions(StateMentions stateMentions) {
        this.stateMentions = stateMentions;
    }

    public Integer getPropagandaCount() {
        return propagandaCount;
    }

    public void setPropagandaCount(Integer propagandaCount) {
        this.propagandaCount = propagandaCount;
    }

    public Integer getProProtestCount() {
        return proProtestCount;
    }

    public void setProProtestCount(Integer proProtestCount) {
        this.proProtestCount = proProtestCount;
    }
}