package com.pumpaj.evropo.repository;

import com.pumpaj.evropo.model.Day;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface DayRepository extends MongoRepository<Day, String> {
    Optional<Day> findByDate(String date);
}