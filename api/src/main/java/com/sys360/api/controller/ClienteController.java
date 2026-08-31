package com.sys360.api.controller;

import com.sys360.api.modelo.Cliente;
import com.sys360.api.repository.ClienteRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/clientes")
public class ClienteController {

    @Autowired
    private ClienteRepository repository;

    // POST: Cadastra o cliente
    @PostMapping
    public Cliente cadastrar(@RequestBody Cliente cliente) {
        return repository.save(cliente);
    }

    // GET: Lista todos os clientes
    @GetMapping
    public List<Cliente> listar() {
        return repository.findAll();
    }
}