package com.sys360.api.controller;

import com.sys360.api.modelo.Venda;
import com.sys360.api.repository.ItemVendaRepository;
import com.sys360.api.repository.VendaRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("api/vendas")
public class VendaController {
    @Autowired
    private VendaRepository repository;

    // POST para criar a venda
    @PostMapping
    public Venda cadastar(@RequestBody Venda venda){
        // Amarra cada item à esta venda específica para o banco de dados entender a relação
        if (venda.getItens() != null){
            venda.getItens().forEach(item -> item.setVenda(venda));
        }
        // O CascadeType.ALL faz o .save() gravar a venda E os itens de uma vez só!
        return repository.save(venda);

    }

    @GetMapping
    public List<Venda> listar(){
        return repository.findAll();
    }
}
